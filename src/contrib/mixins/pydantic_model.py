from __future__ import annotations

from datetime import datetime
from typing import Literal

from contrib.localization.services import gettext as _
from contrib.pydantic.model import PydanticModel
from contrib.pydantic.types import FileUrl
from contrib.pydantic.types import PhoneNumber
from pydantic import EmailStr
from pydantic import Field


class IdMixin(PydanticModel):
    id: int | None = Field(title=_("Идентификатор записи"), default=None)


class HashMixin(PydanticModel):
    hash: str | None = Field(title=_("Хэш"), default=None)


class PhoneMixin(PydanticModel):
    phone: PhoneNumber | None = Field(title=_("Телефон"), default=None)


class EmailMixin(PydanticModel):
    email: Literal[""] | EmailStr | None = Field(title=_("E-mail"), default=None)


class NameMixin(PydanticModel):
    name: str | None = Field(title=_("Наименование"), default=None)


class DeleteMixin(IdMixin):
    delete: bool | None = Field(title=_("Удалить"), default=False)


class DescriptionMixin(PydanticModel):
    description: str | None = Field(title=_("Описание"), default=None)


class IsActiveMixin(PydanticModel):
    is_active: bool | None = Field(title=_("Признак активности записи"), default=None)


class DictionaryMixin(NameMixin, DescriptionMixin):
    pass


class CreatedDatetimeMixin(PydanticModel):
    created_at: datetime | None = Field(title=_("Создан"), default=None)


class UpdatedDatetimeMixin(PydanticModel):
    updated_at: datetime | None = Field(title=_("Изменен"), default=None)


class CreatedUpdatedDatetimeMixin(CreatedDatetimeMixin, UpdatedDatetimeMixin):
    pass


class UserShortInfoDTO(IdMixin, EmailMixin, PhoneMixin, response_model=True, with_paginated=True):
    username: str | None = Field(title=_("Имя пользователя"), default=None)
    first_name: str | None = Field(None, title=_("Имя"))
    last_name: str | None = Field(None, title=_("Фамилия"))
    avatar: FileUrl = Field(title=_("Аватар"), default=None)


class UserShortInfoWithActiveDTO(UserShortInfoDTO, with_paginated=True):
    is_active: bool = Field(title=_("Активен"))


class CreatedUserMixin(PydanticModel):
    created_by: UserShortInfoDTO | None = Field(title=_("Пользователь, создавший запись"), default=None)


class UpdatedUserMixin(PydanticModel):
    updated_by: UserShortInfoDTO | None = Field(title=_("Последний пользователь изменивший запись"), default=None)


class CreatedUpdatedUserMixin(CreatedUserMixin, UpdatedUserMixin):
    pass


class CreatedMixin(CreatedDatetimeMixin, CreatedUserMixin):
    pass


class UpdatedMixin(UpdatedDatetimeMixin, UpdatedUserMixin):
    pass


class CreatedUpdatedMixin(CreatedMixin, UpdatedMixin):
    pass
