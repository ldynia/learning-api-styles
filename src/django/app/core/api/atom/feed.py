from django.contrib.syndication.views import Feed as FeedView
from django.urls import reverse
from django.utils.feedgenerator import Atom1Feed

from core.models import CityRepository


class CityAtomFeedView(FeedView):
    feed_guid = "WFS weather feed"
    feed_type = Atom1Feed
    language = "en-us"
    link = "/forecast/feed"
    subtitle = "One week forecast"
    title = "City Weather Forecast"

    def items(self, city):
        return CityRepository.get_all()

    def item_title(self, city):
        return city.name

    def item_description(self, city):
        return f"{city.name}, {city.country}, {city.region}"

    def item_link(self, city):
        return reverse("city_forecast", args=[city.uuid])

    def item_lastupdated(self, city):
        return city.updated_at
