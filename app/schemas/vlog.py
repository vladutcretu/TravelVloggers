from pydantic import BaseModel, Field, ConfigDict


class CountryBase(BaseModel):
    id: int
    name: str = Field(max_length=50)
    iso_code: str = Field(min_length=2, max_length=2, pattern="^[A-Z]{2}$")


class CountryResponse(CountryBase):
    model_config = ConfigDict(from_attributes=True)


class CountryResponsePaginated(BaseModel):
    countries: list[CountryResponse]
    skip: int
    limit: int
    has_more: bool
