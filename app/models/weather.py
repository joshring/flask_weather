from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from .city import City


class Condition(str, Enum):
    sunny = "sunny"
    cloudy = "cloudy"
    rainy = "rainy"
    snowing = "snowing"
    hailing = "hailing"
    storm = "storm"


class CityWeather(BaseModel):
    model_config = {
        "extra": "forbid",  # disallow extra fields
        "use_enum_values": True,  # str value of enum
    }

    city_name: City
    temperature: float = Field(gt=-90, lt=70)
    condition: Condition
    timestamp: datetime = Field(gt=datetime.fromisoformat("2000-01-01T00:00:00Z"))


class AllCityWeather(BaseModel):
    model_config = {
        "extra": "forbid",  # disallow extra fields
        "use_enum_values": True,  # str value of enum
    }

    all_city_weather: list[CityWeather] = []


# Defining types for request and response, we can later customise these types if we need to
AddCityWeatherReq = CityWeather
AddCityWeatherResp = CityWeather
GetCityWeatherResp = CityWeather
GetAllCityWeather = AllCityWeather
EditCityWeatherReq = CityWeather
EditCityWeatherResp = CityWeather
