import datetime

import grpc
from django.contrib.syndication.views import Feed as FeedView
from django.urls import reverse
from django.utils.feedgenerator import Atom1Feed
from google.protobuf.timestamp_pb2 import Timestamp

import enricher.proto.enricher.v1.enricher_pb2 as pb2
import enricher.proto.enricher.v1.enricher_pb2_grpc as pb2_grpc
from config.base import logger
from core.models import CityRepository
from core.models import WeatherForecastRepository


# tag::define_enriched_view_class[]
class CityAtomFeedEnrichedView(FeedView):
    feed_type = Atom1Feed
    title = "City Weather Forecast Enriched"
    link = "/forecast/feed_enriched"

    channel = grpc.insecure_channel("grpc-server:50051")  # <1>
    stub = pb2_grpc.EnricherServiceStub(channel)  # <1>
# end::define_enriched_view_class[]

    def items(self, city):
        return CityRepository.get_all()

    def item_title(self, city):
        return city.name

    # tag::define_item_description[]
    def item_description(self, city):
        forecast = WeatherForecastRepository.filter(city=city).first()  # <2>
        city_proto = pb2.City(  # <3>
            uuid=str(city.uuid),
            name=city.name,
            country=city.country,
            region=city.region,
        )
        forecast_timestamp = datetime.datetime.combine(  # <4>
            forecast.date, datetime.datetime.min.time()
        )
        timestamp_proto = Timestamp()  # <4>
        timestamp_proto.FromDatetime(forecast_timestamp)  # <4>
        weather_forecast_proto = pb2.WeatherForecast(  # <5>
            city=city_proto,
            timestamp=timestamp_proto,
            rain_sum_mm=forecast.rain_sum_mm,
            showers_sum_mm=forecast.showers_sum_mm,
            snowfall_sum_cm=forecast.snowfall_sum_cm,
            temperature_max_celsius=forecast.temperature_max_celsius,
            temperature_min_celsius=forecast.temperature_min_celsius,
        )
        request = pb2.EnrichRequest(weather_forecast=weather_forecast_proto)  # <6>
        try:
            response = self.stub.Enrich(request, wait_for_ready=True)  # <7>
        except grpc.RpcError as rpc_error:
            logger.exception(f"gRPC call error: {rpc_error}")
            raise

        return response.content  # <8>
    # end::define_item_description[]

    def item_link(self, city):
        return reverse("city_forecast", args=[city.uuid])

    def item_lastupdated(self, city):
        return city.updated_at
