from behave import then
from behave import when


# Scenario: Retrieve the weather forecast as an Atom feed.
@given("the URL to the weather forecast's Atom feed")
def scenario_given(context):
    context.URL_ATOM_FEED = "/forecast/feed"


@when("the feed is requested")
def scenario_when(context):
    context.response = context.client.get(context.URL_ATOM_FEED)


@then("the feed is returned successfully")
def scenario_then(context):
    context.test.assertEqual(context.response.status_code, 200)


@then("it is in Atom feed format")
def scenario_then(context):
    mime_type = context.response.headers["Content-Type"]
    context.test.assertIn("application/atom+xml", mime_type)

    body = context.response.content.decode()
    context.test.assertIn("http://www.w3.org/2005/Atom", body)
