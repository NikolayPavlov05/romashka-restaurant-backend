from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from collections.abc import Callable
from http import HTTPStatus
from typing import Any

import pytest
from contrib.clean_architecture.consts import CleanMethods
from contrib.clean_architecture.consts import ViewActionAttrs
from contrib.clean_architecture.tests.utils import set_user_context
from contrib.clean_architecture.utils.method import clean_method
from contrib.clean_architecture.utils.method import CleanMethodMixin
from contrib.clean_architecture.views.bases import CleanViewSet
from contrib.subclass_control.mixins import RequiredAttrsMixin
from django.db.models import Max
from django.db.models import Model
from django.test.client import RequestFactory
from django.urls import reverse
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate


class BaseViewSetTestMixin(RequiredAttrsMixin, CleanMethodMixin, ABC):
    view_class: CleanViewSet
    model: type[Model]

    request_factory_class: type[RequestFactory] = APIRequestFactory

    test_decorators: tuple[Callable] = (pytest.mark.django_db,)

    def __init_subclass__(cls, view_set_base: bool = False, **kwargs):
        super().__init_subclass__(**kwargs)

        # Оборачивает все clean_methods требуемыми декораторами
        if not view_set_base:
            cls._wrap_methods()

    @classmethod
    def get_test_decorators(cls):
        return cls.test_decorators

    @classmethod
    def _get_method_attr(cls, method_name: str, attr_name: str, result: str = None):
        """Возвращает значение атрибута метода

        Args:
            method_name: Имя метода
            attr_name: Имя атрибута

        Returns:

        """
        attr_full_name = f"get_{method_name}"
        if result:
            attr_full_name = f"{attr_full_name}_{result}"
        attr_full_name = f"{attr_full_name}_test_{attr_name}"

        get_method_attr = getattr(cls, attr_full_name, None)
        return get_method_attr() if get_method_attr else getattr(cls, f"{method_name}_{attr_name}", None)

    @classmethod
    def _wrap_methods(cls):
        for method_attr_name, method in cls.clean_methods.items():
            method_name = method.__method_name__
            result = method_attr_name.split("_")[-1]

            decorators = cls._get_method_attr(method_name, ViewActionAttrs.DECORATORS) or ()
            result_decorators = cls._get_method_attr(method_name, ViewActionAttrs.DECORATORS, result) or ()
            test_decorators = cls.get_test_decorators() or ()

            for decorator in decorators + result_decorators + test_decorators:
                method = decorator(method)

            setattr(cls, method_attr_name, method)

    @classmethod
    def get_view_name(cls, method: str) -> str:
        view_name = cls.view_class.get_snake_view_name_by_class()
        method_name = getattr(cls.view_class, f"get_{method}_url_name")()
        return f"{view_name}-{method_name}"

    def make_request(
        self,
        method: str,
        http_method: str,
        *args,
        request_factory: RequestFactory = None,
        view: Any = None,
        view_name: str = None,
        actions: dict = None,
        data: dict = None,
        format: str = None,
        auth_user: Any = True,
        **kwargs,
    ) -> Any:
        request_factory = request_factory or self.request_factory_class()
        if not view:
            view = self.view_class.as_view(actions=actions or {"get": f"{method}_action"})

        url = reverse(view_name or self.get_view_name(method), args=args, kwargs=kwargs)
        request = getattr(request_factory, http_method)(url, data=data, format=format)

        if auth_user:
            force_authenticate(request, auth_user)
            set_user_context(auth_user)

        return view(request, **kwargs)


class CreateCleanViewSetTestMixin(BaseViewSetTestMixin, required_attrs_base=True):
    required_attrs = ("view_class", "model")

    create_method: str = CleanMethods.CREATE

    create_test_decorators: tuple[Callable] = ()
    create_valid_test_decorators: tuple[Callable] = ()
    create_invalid_test_decorators: tuple[Callable] = ()

    create_actions = {"post": "create_action"}
    create_view_name: str | None = None

    @classmethod
    def get_create_test_decorators(cls):
        return cls.create_test_decorators

    @classmethod
    def get_create_valid_test_decorators(cls):
        return cls.create_valid_test_decorators

    @classmethod
    def get_create_invalid_test_decorators(cls):
        return cls.create_invalid_test_decorators

    @abstractmethod
    def get_create_valid_request_data(self, *args, **kwargs):
        """Фикстура возвращающая валидные данные запроса"""

    @abstractmethod
    def get_create_invalid_request_data(self, *args, **kwargs):
        """Фикстура возвращающая НЕ валидные данные запроса"""

    @abstractmethod
    def get_create_valid_request_user(self, *args, **kwargs):
        """Фикстура возвращающая валидного пользователя запроса"""

    @abstractmethod
    def get_create_invalid_request_user(self, *args, **kwargs):
        """Фикстура возвращающая НЕ валидного пользователя запроса"""

    @pytest.fixture()
    def get_create_valid_request_url_parameters(self, *args, **kwargs):
        """Фикстура возвращающая валидные параметры"""
        return {}

    @pytest.fixture()
    def get_create_invalid_request_url_parameters(self, *args, **kwargs):
        """Фикстура возвращающая невалидные параметры"""
        return {}

    @clean_method(name=CleanMethods.CREATE)
    def test_create_valid(
        self,
        get_create_valid_request_data,
        get_create_valid_request_user,
        get_create_valid_request_url_parameters,
    ):
        response = self.make_request(
            self.create_method,
            "post",
            data=get_create_valid_request_data,
            auth_user=get_create_valid_request_user,
            actions=self.create_actions,
            format="json",
            view_name=self.create_view_name,
            **get_create_valid_request_url_parameters,
        )
        assert response.status_code == HTTPStatus.CREATED
        assert self.model.objects.filter(pk=response.data).exists()

        self.create_valid_assert_result(response)

    def create_valid_assert_result(self, result: Any):
        """Дополнительные assert"""

    @clean_method(name=CleanMethods.CREATE)
    def test_create_invalid(
        self,
        get_create_invalid_request_data,
        get_create_invalid_request_user,
        get_create_invalid_request_url_parameters,
    ):
        if not get_create_invalid_request_data:
            return
        response = self.make_request(
            self.create_method,
            "post",
            data=get_create_invalid_request_data,
            auth_user=get_create_invalid_request_user,
            actions=self.create_actions,
            view_name=self.create_view_name,
            **get_create_invalid_request_url_parameters,
        )
        assert response.status_code != HTTPStatus.CREATED
        self.create_valid_assert_result(response)

    def create_invalid_assert_result(self, result: Any):
        """Дополнительные assert"""


class DetailByPKViewSetTestMixin(BaseViewSetTestMixin, required_attrs_base=True):
    required_attrs = ("view_class", "model")

    detail_by_pk_method: str = CleanMethods.DETAIL_BY_PK

    detail_by_pk_test_decorators: tuple[Callable] = ()
    detail_by_pk_valid_test_decorators: tuple[Callable] = ()
    detail_by_pk_invalid_test_decorators: tuple[Callable] = ()

    detail_by_pk_view_name: str | None = None
    detail_by_pk_actions: dict = {"get": "detail_by_pk_action"}

    @classmethod
    def get_detail_by_pk_test_decorators(cls):
        return cls.detail_by_pk_test_decorators

    @classmethod
    def get_detail_by_pk_valid_test_decorators(cls):
        return cls.detail_by_pk_valid_test_decorators

    @classmethod
    def get_detail_by_pk_invalid_test_decorators(cls):
        return cls.detail_by_pk_invalid_test_decorators

    @abstractmethod
    def get_detail_by_pk_valid_request_data(self, *args, **kwargs):
        """Фикстура возвращающая валидные данные запроса"""

    @pytest.fixture()
    def get_detail_by_pk_invalid_request_data(self, *args, **kwargs):
        max_id = self.model.objects.aggregate(max_id=Max("id", default=0)).get("max_id")
        return max_id + 1

    @abstractmethod
    def get_detail_by_pk_valid_request_user(self, *args, **kwargs):
        """Фикстура возвращающая валидного пользователя запроса"""

    @abstractmethod
    def get_detail_by_pk_invalid_request_user(self, *args, **kwargs):
        """Фикстура возвращающая НЕ валидного пользователя запроса"""

    @clean_method(name=CleanMethods.DETAIL_BY_PK)
    def test_detail_by_pk_valid(self, get_detail_by_pk_valid_request_data, get_detail_by_pk_valid_request_user):
        response = self.make_request(
            self.detail_by_pk_method,
            "get",
            auth_user=get_detail_by_pk_valid_request_user,
            actions=self.detail_by_pk_actions,
            pk=get_detail_by_pk_valid_request_data,
            view_name=self.detail_by_pk_view_name,
        )
        assert response.status_code == HTTPStatus.OK, response.data
        assert get_detail_by_pk_valid_request_data == response.data["id"]
        self.detail_by_pk_valid_assert_result(response)

    def detail_by_pk_valid_assert_result(self, result: Any):
        """Дополнительные assert"""

    @clean_method(name=CleanMethods.DETAIL_BY_PK)
    def test_detail_by_pk_invalid(
        self,
        get_detail_by_pk_invalid_request_data,
        get_detail_by_pk_invalid_request_user,
    ):
        response = self.make_request(
            self.detail_by_pk_method,
            "get",
            auth_user=get_detail_by_pk_invalid_request_user,
            actions=self.detail_by_pk_actions,
            pk=get_detail_by_pk_invalid_request_data,
            view_name=self.detail_by_pk_view_name,
        )
        assert response.status_code != HTTPStatus.OK
        self.detail_by_pk_invalid_assert_result(response)

    def detail_by_pk_invalid_assert_result(self, result: Any):
        """Дополнительные assert"""


class DetailViewSetTestMixin(BaseViewSetTestMixin, required_attrs_base=True):
    required_attrs = ("view_class", "model")

    detail_method: str = CleanMethods.DETAIL
    detail_actions: dict = {"get": "detail_action"}

    detail_test_decorators: tuple[Callable] = ()
    detail_valid_test_decorators: tuple[Callable] = ()
    detail_invalid_test_decorators: tuple[Callable] = ()

    detail_view_name: str | None = None
    detail_use_invalid: bool = True

    @classmethod
    def get_detail_test_decorators(cls):
        return cls.detail_test_decorators

    @classmethod
    def get_detail_valid_test_decorators(cls):
        return cls.detail_valid_test_decorators

    @classmethod
    def get_detail_invalid_test_decorators(cls):
        return cls.detail_invalid_test_decorators

    @abstractmethod
    def get_detail_valid_request_data(self, *args, **kwargs):
        """Фикстура возвращающая валидные данные запроса"""

    @pytest.fixture()
    def get_detail_invalid_request_data(self, *args, **kwargs):
        """Фикстура для невалиданых данных запроса"""

    @pytest.fixture()
    def get_detail_valid_response_data(self, *args, **kwargs):
        """Фикстура возвращающая валидные ответы запроса"""

    @pytest.fixture()
    def get_detail_valid_request_user(self, *args, **kwargs):
        """Фикстура возвращающая валидного пользователя запроса"""

    @pytest.fixture()
    def get_detail_invalid_request_user(self, *args, **kwargs):
        """Фикстура возвращающая НЕ валидного пользователя запроса"""

    @clean_method(name=CleanMethods.DETAIL_BY_PK)
    def test_detail_valid(
        self,
        get_detail_valid_response_data,
        get_detail_valid_request_data,
        get_detail_valid_request_user,
    ):
        response = self.make_request(
            self.detail_method,
            "get",
            auth_user=get_detail_valid_request_user,
            actions=self.detail_actions,
            data=get_detail_valid_request_data,
            view_name=self.detail_view_name,
            **self.detail_valid_kwargs,
        )
        assert response.status_code == HTTPStatus.OK, response.data
        assert get_detail_valid_response_data == response.data["id"]
        self.detail_valid_assert_result(response)

    def detail_valid_assert_result(self, result: Any):
        """Дополнительные assert"""

    @property
    def detail_invalid_kwargs(self):
        return {}

    @property
    def detail_valid_kwargs(self):
        return {}

    @clean_method(name=CleanMethods.DETAIL_BY_PK)
    def test_detail_invalid(self, get_detail_invalid_request_data, get_detail_invalid_request_user):
        if not self.detail_use_invalid:
            return
        response = self.make_request(
            self.detail_method,
            "get",
            auth_user=get_detail_invalid_request_user,
            actions=self.detail_actions,
            data=get_detail_invalid_request_data,
            view_name=self.detail_view_name,
            **self.detail_invalid_kwargs,
        )
        assert response.status_code != HTTPStatus.OK
        self.detail_invalid_assert_result(response)

    def detail_invalid_assert_result(self, result: Any):
        """Дополнительные assert"""


class DeleteViewSetTestMixin(BaseViewSetTestMixin, required_attrs_base=True):
    required_attrs = ("view_class", "model")

    delete_method: str = CleanMethods.DELETE

    delete_test_decorators: tuple[Callable] = ()
    delete_valid_test_decorators: tuple[Callable] = ()
    delete_invalid_test_decorators: tuple[Callable] = ()

    delete_view_name: str | None = None
    delete_actions: dict = {"delete": "delete_action"}

    @classmethod
    def get_delete_test_decorators(cls):
        return cls.delete_test_decorators

    @classmethod
    def get_delete_valid_test_decorators(cls):
        return cls.delete_valid_test_decorators

    @classmethod
    def get_delete_invalid_test_decorators(cls):
        return cls.delete_invalid_test_decorators

    @abstractmethod
    def get_delete_valid_request_data(self, *args, **kwargs):
        """Фикстура возвращающая валидные данные запроса"""

    @abstractmethod
    def get_delete_invalid_request_data(self, *args, **kwargs):
        """Фикстура возвращающая НЕ валидные данные запроса"""

    @abstractmethod
    def get_delete_valid_request_user(self, *args, **kwargs):
        """Фикстура возвращающая валидного пользователя запроса"""

    @abstractmethod
    def get_delete_invalid_request_user(self, *args, **kwargs):
        """Фикстура возвращающая НЕ валидного пользователя запроса"""

    @clean_method(name=CleanMethods.DELETE)
    def test_delete_valid(self, get_delete_valid_request_data, get_delete_valid_request_user):
        response = self.make_request(
            self.delete_method,
            "delete",
            auth_user=get_delete_valid_request_user,
            actions=self.delete_actions,
            pk=get_delete_valid_request_data,
            view_name=self.delete_view_name,
        )
        assert response.status_code == HTTPStatus.ACCEPTED
        self.delete_valid_assert_result(response)

    def delete_valid_assert_result(self, result: Any):
        """Дополнительные assert"""

    @clean_method(name=CleanMethods.DELETE)
    def test_delete_invalid(self, get_delete_invalid_request_data, get_delete_invalid_request_user):
        response = self.make_request(
            self.delete_method,
            "get",
            auth_user=get_delete_invalid_request_user,
            actions=self.delete_actions,
            pk=get_delete_invalid_request_data,
            view_name=self.delete_view_name,
        )
        assert response.status_code != HTTPStatus.OK
        assert self.model.objects.filter(id=get_delete_invalid_request_data).exists()
        self.delete_valid_assert_result(response)

    def delete_invalid_assert_result(self, result: Any):
        """Дополнительные assert"""


class UpdateViewSetTestMixin(BaseViewSetTestMixin, required_attrs_base=True):
    required_attrs = ("view_class", "model")

    update_method: str = CleanMethods.UPDATE

    update_test_decorators: tuple[Callable] = ()
    update_valid_test_decorators: tuple[Callable] = ()
    update_invalid_test_decorators: tuple[Callable] = ()

    update_assert_fields: list[str] = []
    update_assert_m2m_fields: list[str] = []

    @classmethod
    def get_update_test_decorators(cls):
        return cls.update_test_decorators

    @classmethod
    def get_update_valid_test_decorators(cls):
        return cls.update_valid_test_decorators

    @classmethod
    def get_update_invalid_test_decorators(cls):
        return cls.update_invalid_test_decorators

    @abstractmethod
    def get_update_valid_request_data(self, *args, **kwargs):
        """Фикстура возвращающая валидные данные запроса"""

    @abstractmethod
    def get_update_invalid_request_data(self, *args, **kwargs):
        """Фикстура возвращающая невалидные данные запроса"""

    @abstractmethod
    def get_update_valid_request_user(self, *args, **kwargs):
        """Фикстура возвращающая валидного пользователя запроса"""

    @abstractmethod
    def get_update_invalid_request_user(self, *args, **kwargs):
        """Фикстура возвращающая НЕ валидного пользователя запроса"""

    def update_valid_assert_fields(self, object_id: int, update_data: dict):
        object = self.model.objects.get(pk=object_id)
        for field in self.update_assert_fields:
            assert getattr(object, field) == update_data[field]

        for field in self.update_assert_m2m_fields:
            objects_m2m_field = getattr(object, field).values_list("id", flat=True)
            for m2m_update_obj in update_data[field]:
                if m2m_update_obj.get("delete", False):
                    assert m2m_update_obj["id"] not in objects_m2m_field
                else:
                    assert m2m_update_obj["id"] in objects_m2m_field

    @clean_method(name=CleanMethods.UPDATE)
    def test_update_valid(self, get_update_valid_request_data, get_update_valid_request_user):
        response = self.make_request(
            self.update_method,
            "patch",
            data=get_update_valid_request_data,
            auth_user=get_update_valid_request_user,
            actions={"patch": "update_action"},
            pk=get_update_valid_request_data["id"],
            format="json",
        )
        assert response.status_code == HTTPStatus.ACCEPTED
        self.update_valid_assert_fields(get_update_valid_request_data["id"], get_update_valid_request_data)
        self.update_valid_assert_result(response)

    def update_valid_assert_result(self, result: Any):
        """Дополнительные assert"""

    @clean_method(name=CleanMethods.UPDATE)
    def test_update_invalid(self, get_update_invalid_request_data, get_update_invalid_request_user):
        response = self.make_request(
            self.update_method,
            "patch",
            data=get_update_invalid_request_data,
            auth_user=get_update_invalid_request_user,
            actions={"patch": "update_action"},
            pk=get_update_invalid_request_data["id"],
            format="json",
        )
        assert response.status_code != HTTPStatus.OK
        self.update_valid_assert_result(response)

    def update_invalid_assert_result(self, result: Any):
        """Дополнительные assert"""


class PatchListViewSetTestMixin(BaseViewSetTestMixin, required_attrs_base=True):
    required_attrs = ("view_class", "model")

    update_method: str = CleanMethods.UPDATE

    patch_list_test_decorators: tuple[Callable] = ()
    patch_list_valid_test_decorators: tuple[Callable] = ()
    patch_list_invalid_test_decorators: tuple[Callable] = ()

    patch_list_assert_fields: list[str] = []
    patch_list_view_name: str | None = None

    @classmethod
    def get_patch_list_test_decorators(cls):
        return cls.patch_list_test_decorators

    @classmethod
    def get_patch_list_valid_test_decorators(cls):
        return cls.patch_list_valid_test_decorators

    @classmethod
    def get_patch_list_invalid_test_decorators(cls):
        return cls.patch_list_invalid_test_decorators

    @abstractmethod
    def get_patch_list_valid_request_data(self, *args, **kwargs):
        """Фикстура возвращающая валидные данные запроса"""

    @abstractmethod
    def get_patch_list_invalid_request_data(self, *args, **kwargs):
        """Фикстура возвращающая невалидные данные запроса"""

    @abstractmethod
    def get_patch_list_valid_url_parameters(self, *args, **kwargs):
        """Фикстура возвращающая валидные параметры ссылки запросы"""

    @abstractmethod
    def get_patch_list_invalid_url_parameters(self, *args, **kwargs):
        """Фикстура возвращающая НЕ валидные параметры ссылки запросы"""

    @abstractmethod
    def get_patch_list_valid_request_user(self, *args, **kwargs):
        """Фикстура возвращающая валидного пользователя запроса"""

    @abstractmethod
    def get_patch_list_invalid_request_user(self, *args, **kwargs):
        """Фикстура возвращающая НЕ валидного пользователя запроса"""

    def patch_list_valid_assert_fields(self, update_data: dict):
        objects = self.model.objects.filter(pk__in=[data["id"] for data in update_data["items"]])
        objects_by_pk = {item.id: item for item in objects}
        for data in update_data["items"]:
            if data.get("delete", False):
                assert data["id"] not in objects_by_pk
            else:
                for field in self.patch_list_assert_fields:
                    if data.get(field, None) is None:
                        continue
                    assert getattr(objects_by_pk[data["id"]], field) == data.get(field, None)

    @clean_method(name=CleanMethods.PATCH_LIST)
    def test_patch_list_valid(
        self,
        get_patch_list_valid_request_data,
        get_patch_list_valid_request_user,
        get_patch_list_valid_url_parameters,
    ):
        response = self.make_request(
            self.update_method,
            "patch",
            data=get_patch_list_valid_request_data,
            auth_user=get_patch_list_valid_request_user,
            actions={"patch": "update_action"},
            format="json",
            view_name=self.patch_list_view_name,
            **get_patch_list_valid_url_parameters,
        )
        assert response.status_code == HTTPStatus.ACCEPTED
        self.patch_list_valid_assert_fields(get_patch_list_valid_request_data)
        self.patch_list_valid_assert_result(response)

    def patch_list_valid_assert_result(self, result: Any):
        """Дополнительные assert"""

    @clean_method(name=CleanMethods.PATCH_LIST)
    def test_patch_list_invalid(
        self,
        get_patch_list_invalid_request_data,
        get_patch_list_invalid_request_user,
        get_patch_list_invalid_url_parameters,
    ):
        response = self.make_request(
            self.update_method,
            "patch",
            data=get_patch_list_invalid_request_data,
            auth_user=get_patch_list_invalid_request_user,
            actions={"patch": "update_action"},
            format="json",
            view_name=self.patch_list_view_name,
            **get_patch_list_invalid_url_parameters,
        )
        assert response.status_code != HTTPStatus.ACCEPTED
        self.patch_list_invalid_assert_result(response)

    def patch_list_invalid_assert_result(self, result: Any):
        """Дополнительные assert"""


class SearchViewSetTestMixin(BaseViewSetTestMixin, required_attrs_base=True):
    required_attrs = ("view_class", "model")

    search_method: str = CleanMethods.SEARCH

    search_test_decorators: tuple[Callable] = ()

    search_text: str

    search_view_name: str | None = None

    @classmethod
    def get_search_test_decorators(cls):
        return cls.search_test_decorators

    @abstractmethod
    def get_search_valid_request_obj(self, *args, **kwargs):
        """Фикстура возвращающая объект, которые мы должны получить после поиска"""

    @abstractmethod
    def get_search_invalid_request_obj(self, *args, **kwargs):
        """Фикстура возвращающая объект, которые мы НЕ должны получить после поиска"""

    @abstractmethod
    def get_search_request_user(self, *args, **kwargs):
        """Фикстура возвращающая валидного пользователя запроса"""

    def prepare_search(self): ...

    @clean_method(name=CleanMethods.SEARCH)
    def test_search(
        self,
        get_search_valid_request_obj,
        get_search_invalid_request_obj,
        get_search_request_user,
    ):
        self.prepare_search()
        response = self.make_request(
            self.search_method,
            "get",
            data={"search": self.search_text},
            auth_user=get_search_request_user,
            actions={"get": "search_action"},
            view_name=self.search_view_name,
        )
        assert response.status_code == HTTPStatus.OK
        assert any(get_search_valid_request_obj.id == entry["id"] for entry in response.data["results"])
        assert all(get_search_invalid_request_obj.id != entry["id"] for entry in response.data["results"])
        self.search_assert_result(response)

    def search_assert_result(self, result: Any):
        """Дополнительные assert"""


class RetrieveViewSetTestMixin(BaseViewSetTestMixin, required_attrs_base=True):
    required_attrs = ("view_class", "model")

    retrieve_method: str = CleanMethods.RETRIEVE
    retrieve_test_decorators: tuple[Callable] = ()
    retrieve_view_name: str | None = None
    retrieve_actions: dict = {"get": "retrieve_action"}

    @classmethod
    def get_retrieve_test_decorators(cls):
        return cls.retrieve_test_decorators

    @abstractmethod
    def get_retrieve_valid_request_obj(self, *args, **kwargs):
        """Фикстура возвращающая объект, которые мы должны получить после поиска"""

    @abstractmethod
    def get_retrieve_invalid_request_obj(self, *args, **kwargs):
        """Фикстура возвращающая объект, которые мы НЕ должны получить после поиска"""

    @abstractmethod
    def get_retrieve_request_user(self, *args, **kwargs):
        """Фикстура возвращающая валидного пользователя запроса"""

    @abstractmethod
    def get_retrieve_request_data(self, *args, **kwargs):
        """Фикстура возвращающая данные для фильтрации запроса"""

    @pytest.fixture()
    def get_retrieve_request_url_parameters(self, *args, **kwargs):
        """Фикстура возвращающая данные для параметров ссылки запроса"""
        return {}

    @clean_method(name=CleanMethods.RETRIEVE)
    def test_retrieve(
        self,
        get_retrieve_valid_request_obj,
        get_retrieve_invalid_request_obj,
        get_retrieve_request_user,
        get_retrieve_request_data,
        get_retrieve_request_url_parameters,
    ):
        response = self.make_request(
            self.retrieve_method,
            "get",
            data=get_retrieve_request_data,
            auth_user=get_retrieve_request_user,
            actions=self.retrieve_actions,
            view_name=self.retrieve_view_name,
            **get_retrieve_request_url_parameters,
        )
        assert response.status_code == HTTPStatus.OK
        assert any(get_retrieve_valid_request_obj.id == entry["id"] for entry in response.data["results"])
        if get_retrieve_invalid_request_obj:
            assert all(get_retrieve_invalid_request_obj.id != entry["id"] for entry in response.data["results"])
        self.retrieve_assert_result(response)

    def retrieve_assert_result(self, result: Any):
        """Дополнительные assert"""
