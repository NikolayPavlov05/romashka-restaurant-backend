from __future__ import annotations

import logging
import traceback as _traceback
from abc import ABC
from collections.abc import Callable
from copy import deepcopy
from logging import getLogger
from logging import Logger
from typing import Any
from typing import Self
from typing import TYPE_CHECKING

from django.conf import settings
from contrib.localization.services import gettext as _
from contrib.rest.client.interfaces import IRestClient
from contrib.rest.config import RestConfig
from contrib.rest.enums import TokenTypes
from contrib.rest.exceptions import RestMaxRetriesException
from contrib.rest.exceptions import RestRequestException
from contrib.rest.schemas import RestMethodResponse
from contrib.rest.schemas import RestRedirectMixin
from contrib.subclass_control.mixins import SingletonMixin
from requests import Response
from requests import Session
from requests.cookies import cookiejar_from_dict

if TYPE_CHECKING:
    from contrib.rest.method import RestMethod
    from contrib.rest.models import RestLog


class RestClient(SingletonMixin, IRestClient, ABC, singleton_args=("config",)):
    class __RetryRequest(Exception):
        pass

    __services__: list[RestClientService]
    __default_config_class__: type[RestConfig] = RestConfig

    _DEFAULT_TEST_RESPONSE: Any = None
    _DEFAULT_TEST_RESPONSE_FACTORY: Callable = lambda: None

    _config: RestConfig | None = None
    _session: Session | None = None

    logger: Logger = None
    model_logger: type[RestLog] = None

    def __init_subclass__(cls, config_class: type[RestConfig] | None = None, **kwargs):
        super().__init_subclass__(**kwargs)
        if config_class is not None:
            cls.__default_config_class__ = config_class

    def __init__(
        self,
        config: RestConfig = None,
        *,
        logger: str | Logger = logging,
        model_logger: type[RestLog] = None,
        **kwargs,
    ):
        for service in self.__services__:
            service.client = self

        if config is None:
            config = self.__class__.__default_config_class__()
        self._config = config

        if isinstance(logger, str):
            logger = getLogger(logger)

        if logger:
            self.logger = logger
        if model_logger is not None:
            self.model_logger = model_logger

        if settings.TEST_MODE and self.config.SKIP_FOR_TEST_MODE:
            return

        self.__init_client__()
        self.__post_init_client__()
        if self._config.NEED_AUTHENTICATION:
            self._authenticate(raise_exceptions=False)

    def __init_client__(self):
        session = Session()
        session.headers = self.config.HEADERS
        session.proxies = self.config.PROXIES
        session.hooks = self.config.HOOKS
        session.params = self.config.PARAMS
        session.stream = self.config.STREAM
        session.verify = self.config.VERIFY
        session.cert = self.config.CERT
        session.max_redirects = self.config.MAX_REDIRECTS
        session.cookies = cookiejar_from_dict(self.config.COOKIES)

        if self.config.TOKEN:
            if self.config.TOKEN_TYPE == TokenTypes.JWT:
                session.headers["authorization"] = f"token {self.config.TOKEN}"
            elif self.config.TOKEN_TYPE == TokenTypes.BEARER:
                session.headers["authorization"] = f"Bearer {self.config.TOKEN}"
            if not self.config.TOKEN_TYPE:
                session.headers["authorization"] = self.config.TOKEN
        elif self.config.USERNAME and self.config.PASSWORD:
            session.auth = (self.config.USERNAME, self.config.PASSWORD)
        if self.config.API_KEY:
            session.headers["x-api-key"] = self.config.API_KEY

        self._session = session

    def __post_init_client__(self):
        pass

    def _authenticate(self, *, raise_exceptions: bool = True):
        pass

    def _prepare_request_kwargs(self, request_kwargs: dict[str, Any], extra_kwargs: dict[str, Any]):
        pass

    def _prepare_response(self, response: Response, method: RestMethod):
        return method.response_type.model_validate(response, from_attributes=True)

    def _validate_raw_response(self, response: Response, method: RestMethod):
        pass

    def _validate_method_response(self, response: RestMethodResponse, method: RestMethod):
        if method.validator:
            method.validator(response)

    def _validate_response(self, response: RestMethodResponse):
        if not response.ok:
            raise RestRequestException(response.text)

    def _finalize_response(self, response: RestMethodResponse):
        return response

    def _retry_request(self):
        raise self.__RetryRequest

    def _get_test_response(self, method: RestMethod, raise_exceptions: bool = True, **kwargs):
        response_type = method.response_type
        if factory := getattr(response_type, "factory", None):
            return factory.build()
        elif self._DEFAULT_TEST_RESPONSE:
            return self._DEFAULT_TEST_RESPONSE
        elif self._DEFAULT_TEST_RESPONSE_FACTORY:
            return self.__class__._DEFAULT_TEST_RESPONSE_FACTORY()
        return

    def _make_redirect(self, response: Response, method: RestMethod, request_kwargs: dict[str, Any]):
        return method.response_type(url=f"{response.url}?{response.request.body}")

    def _make_request(
        self,
        method: RestMethod,
        *,
        paths: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
        data: Any = None,
        extra_kwargs: dict[str, Any] | None = None,
        raise_exceptions: bool = True,
        **kwargs,
    ):
        request_kwargs = {"data": data or body, **kwargs}
        self._prepare_request_kwargs(request_kwargs, extra_kwargs)
        try:
            url = f"{self.config.url}/{method.path}"
            if paths:
                url = url.format(**paths)

            request_method = getattr(self._session, method.method.lower())
            response = request_method(url, **request_kwargs)
        except Exception as err:
            self.logging(
                message=_("Ошибка при выполнении запроса"),
                traceback=_traceback.format_exc(),
                params=request_kwargs,
                method=method,
            )
            if raise_exceptions:
                raise err
            return

        try:
            self._validate_raw_response(response, method)

            if response.ok and issubclass(method.response_type, RestRedirectMixin):
                return self._make_redirect(response, method, request_kwargs)

            response = self._prepare_response(response, method)
            self._validate_response(response)
            self._validate_method_response(response, method)
            response = self._finalize_response(response)
            return response
        except self.__RetryRequest:
            raise self.__RetryRequest
        except Exception as err:
            self.logging(
                message=_("Ошибка при обработке ответа"),
                traceback=_traceback.format_exc(),
                params=request_kwargs,
                response=response.text,
                method=method,
            )
            if raise_exceptions:
                raise err
            return

    def make_request(
        self,
        method: RestMethod,
        *,
        raise_exceptions: bool = True,
        __retry_number: int = 0,
        **kwargs,
    ):
        if settings.TEST_MODE and self.config.SKIP_FOR_TEST_MODE:
            return self._get_test_response(method, raise_exceptions=raise_exceptions, **kwargs)

        if __retry_number > self._config.MAX_RETRY_COUNT:
            self.logging(
                message=_("Превышено количество попыток выполнения запроса"),
                params=kwargs,
                method=method,
            )
            if raise_exceptions:
                raise RestMaxRetriesException(method.path)
            return

        kwargs_copy = deepcopy(kwargs)

        try:
            return self._make_request(method, raise_exceptions=raise_exceptions, **kwargs)
        except self.__RetryRequest:
            return self.make_request(
                method,
                raise_exceptions=raise_exceptions,
                _RestClient__retry_number=__retry_number + 1,
                **kwargs_copy,
            )

    def logging(
        self,
        message: str = None,
        traceback: str = None,
        params: dict[str, Any] = None,
        response: Any = None,
        method: RestMethod = None,
    ):
        if not self.model_logger and not self.logger:
            return

        if method:
            method = method.path
        if params:
            params = str(params)
        if response:
            response = str(response)

        if self.model_logger:
            self.model_logger.objects.create(
                message=message,
                traceback=traceback,
                params=params,
                response=response,
                method=method,
            )
        if self.logger:
            self.logger.error(
                f"\n\tClient: {self.__class__.__name__}; \n\t"
                f"Method: {method or "-"}; \n\t"
                f"Message: {message or "-"}; \n\t"
                f"Params: {params or "-"}; \n\t"
                f"Response: {response or "-"}; \n\t"
                f"Traceback: {traceback or "-"};"
            )

    @classmethod
    def build_client(
        cls,
        config: RestConfig = None,
        *,
        logger: str | Logger,
        model_logger: type[RestLog] = None,
        **kwargs: Any,
    ) -> Self:
        return cls(config, logger=logger, model_logger=model_logger, **kwargs)

    @property
    def config(self):
        return self._config


class RestClientService[RestClientType: RestClient]:
    client: RestClientType | RestClient | None = None

    def __set_name__(self, owner: RestClientType, name: str):
        if not hasattr(owner, "__services__"):
            owner.__services__ = []
        owner.__services__.append(self)
