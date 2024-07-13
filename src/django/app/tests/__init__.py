from .api.atom.test_forecast_feed import *
from .api.graphql.test_city_mutation import *
from .api.graphql.test_city_query import *
from .api.graphql.test_forecast_query import *
from .api.graphql.test_geocoding_query import *
from .api.graphql.test_weather_history_query import *
# from .api.graphql.test_weather_history_mutation import *
from .api.rest.v1.test_jwt_auth_flowl import *
from .api.rest.v1.test_rest_city_detail import *
from .api.rest.v1.test_rest_city_list import *
from .api.rest.v1.test_rest_geocoding_list import *
from .api.rest.v1.test_rest_weather_list import *
# from .api.rest.v1.test_rest_weather_seed import *
from .api.webhook.test_webhook_v1 import *
from .api.webhook.test_webhook_v2 import *
from .api.webhook.test_webhook_v3 import *
from .api.websocket.v1.test_alert_endpoint import *
from .api.websocket.v1.test_chat_endpoint import *
from .api.websocket.v1.test_echo_endpoint import *
from .cli.test_app_alert import *
from .cli.test_app_cities import *
from .cli.test_app_event import *
# from .cli.test_app_seed import *
from .docs.test_rest_schema import *
from .docs.test_websocket_schema import *
from .env.test_packages import *
from .www.test_frontend_endpoints import *