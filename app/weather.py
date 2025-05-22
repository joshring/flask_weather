from flask import Blueprint, abort, Response
from flask_pydantic import validate
from werkzeug.exceptions import HTTPException
from http import HTTPStatus

bp = Blueprint("weather", __name__)

from .models.city import City
from .models.weather import (
    AddCityWeatherReq,
    AddCityWeatherResp,
    GetCityWeatherResp,
    CityWeather,
    GetAllCityWeather,
    EditCityWeatherReq,
    EditCityWeatherResp,
)

all_city_weather: dict[str, list[CityWeather]] = {}


def is_weather_data_newer(body: CityWeather):
    """
    abort if data not newer than current data
    """
    city_weather = all_city_weather[body.city_name]
    latest_city_weather = city_weather[len(city_weather) - 1]

    if latest_city_weather.timestamp > body.timestamp:
        abort(
            HTTPStatus.BAD_REQUEST,
            description=f"new weather data: {body.timestamp} is older than current data: {latest_city_weather.timestamp}",
        )


@bp.post("/weather")
@validate()
def add_city_weather(body: AddCityWeatherReq) -> AddCityWeatherResp:

    if body.city_name not in all_city_weather:
        all_city_weather[body.city_name] = [body]
    else:
        is_weather_data_newer(body=body)

        all_city_weather[body.city_name].append(body)

    return AddCityWeatherResp(**body.model_dump())


@bp.get("/weather/<city_name>")
@validate()
def get_city_weather(city_name: str) -> GetCityWeatherResp:

    city_weather_list = all_city_weather.get(city_name)
    if city_weather_list is None or len(city_weather_list) == 0:
        abort(HTTPStatus.NOT_FOUND, description="city not found")

    latest_city_weather = city_weather_list[len(city_weather_list) - 1]
    return GetCityWeatherResp(**latest_city_weather.model_dump())


@bp.get("/weather")
@validate()
def get_all_city_weather() -> GetAllCityWeather:

    returnValue = [
        item[len(item) - 1] if len(item) > 0 else [] for item in all_city_weather.values()
    ]

    return GetAllCityWeather(all_city_weather=returnValue)


@bp.delete("/weather/<city_name>")
@validate()
def delete_city_weather(city_name: str) -> GetAllCityWeather:

    city_weather_list = all_city_weather.pop(city_name, None)
    if city_weather_list is None or len(city_weather_list) == 0:
        abort(HTTPStatus.NOT_FOUND, description="city not found")

    return Response(
        None,
        status=HTTPStatus.NO_CONTENT,
    )


@bp.put("/weather/<city_name>")
@validate(body=EditCityWeatherReq)
def edit_city_weather(city_name: str, body: EditCityWeatherReq) -> EditCityWeatherResp:

    city_weather_list = all_city_weather.get(city_name, None)
    if city_weather_list is None or len(city_weather_list) == 0:
        abort(HTTPStatus.NOT_FOUND, description="city not found")

    is_weather_data_newer(body=body)

    city_weather_list.append(body)
    all_city_weather.update({body.city_name: city_weather_list})

    return EditCityWeatherResp(**body.model_dump())
