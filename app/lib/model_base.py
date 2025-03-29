from sqlmodel import SQLModel


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