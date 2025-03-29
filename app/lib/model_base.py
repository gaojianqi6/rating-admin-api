from sqlmodel import SQLModel
from pydantic import BaseModel, ConfigDict


def to_camel(string: str) -> str:
    parts = string.split('_')
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])


class CamelModel(SQLModel):
    # # For Pydantic V1 compatibility
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True

    # For Pydantic V2 compatibility
    # model_config = {
    #     "alias_generator": to_camel,
    #     "populate_by_name": True,
    # }

class APIBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=lambda field_name: ''.join(
            word.capitalize() if i > 0 else word
            for i, word in enumerate(field_name.split('_'))
        ),
        populate_by_name=True
    )