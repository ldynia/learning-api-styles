from behave import given
from behave import then
from behave import when

from core.models import CityRepository
from core.models import CitySeed
from core.models import WeatherForecastSeed


# Scenario: Retrieve the city's weather forecast page as HTML.
@given("a city")
def scenario_given(context):
    CitySeed().seed()
    WeatherForecastSeed().seed()

    context.city_uuid = CityRepository.get_first().uuid


@when("the city's weather forecast page is requested")
def scenario_when(context):
    context.response = context.client.get(f"/forecast/{context.city_uuid}")


@then("the page is loaded successfully")
def scenario_then(context):
    context.test.assertEqual(context.response.status_code, 200)


@then("it is an HTML page")
def scenario_then(context):
    context.test.assertIn("text/html", context.response.headers["Content-Type"])
    context.test.assertIn("<!doctype html>", context.response.content.decode())


# Scenario: Fail to retrieve the weather forecast page for a non-existent city
@given("a non-existent city")
def scenario_given(context):
    context.city_uuid = "123abc"


@when("the non-existent city's weather forecast page is requested")
def scenario_when(context):
    context.response = context.client.get(f"/forecast/{context.city_uuid}")


@then("the page is not found")
def scenario_then(context):
    context.test.assertEqual(context.response.status_code, 404)
