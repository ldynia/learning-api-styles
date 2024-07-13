import datetime

from django.http import Http404
from django.views.generic import ListView

from core.models import WeatherForecast
from core.models import WeatherForecastRepository
from core.models import CityRepository


class WeatherForecastFeedListView(ListView):
    model = WeatherForecast
    context_object_name = "forecast"
    template_name = "feed/forecast.html"

    def get(self, request, *args, **kwargs):
        self.object_list = self.__get_queryset()
        if not self.object_list:
            raise Http404("City not found.")

        context = self.get_context_data()

        return self.render_to_response(context)

    def __get_queryset(self):
        uuid = self.kwargs["city_uuid"]
        city = CityRepository.get_by_id(uuid)
        today = datetime.date.today()

        return WeatherForecastRepository.filter(city=city, date__gte=today)
