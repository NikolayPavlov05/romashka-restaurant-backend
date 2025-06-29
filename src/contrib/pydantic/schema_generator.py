from __future__ import annotations

from pydantic.json_schema import GenerateJsonSchema
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema


class AdaptedGenerateJsonSchema(GenerateJsonSchema):
    """
    Генератор JSON-схемы, адаптированный в части объявления nullable-параметров.

    Используемая версия pydantic генерирует данные для openapi версии 3.1.*, а DRF - 3.0.2.
    Данные версии отличаются, в частности, объявлением необязательных атрибутов.
    """

    def nullable_schema(self, schema: core_schema.NullableSchema) -> JsonSchemaValue:
        inner_json_schema = self.generate_inner(schema["schema"])
        return {"nullable": True, **self.get_flattened_anyof([inner_json_schema])}

    def is_instance_schema(self, schema: core_schema.IsInstanceSchema) -> JsonSchemaValue:
        return super().is_instance_schema(schema)
