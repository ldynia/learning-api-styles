from strawberry import UNSET


def notmalize_history_ordring(order):
    sortings = {
        "date": order.date.value if order.date != UNSET else None,
        "rain_sum_mm": order.rain_sum_mm.value if order.rain_sum_mm != UNSET else None,
        "snowfall_sum_cm": order.snowfall_sum_cm.value if order.snowfall_sum_cm != UNSET else None,
        "sunrise_iso8601": order.sunrise_iso8601.value if order.sunrise_iso8601 != UNSET else None,
        "sunset_iso8601": order.sunset_iso8601.value if order.sunset_iso8601 != UNSET else None,
        "temperature_max_celsius": order.temperature_max_celsius.value if order.temperature_max_celsius != UNSET else None,
        "temperature_min_celsius": order.temperature_min_celsius.value if order.temperature_min_celsius != UNSET else None,
        "wind_speed_max_kmh": order.wind_speed_max_kmh.value if order.wind_speed_max_kmh != UNSET else None,
    }

    # Normalize sortings dict so it's prefixed with '-' for DESC
    signed_sortings_normalized = {}
    for key, val in sortings.items():
        if val is not None:
            if val == "DESC":
                signed_sortings_normalized[f"-{key}"] = val
            else:
                signed_sortings_normalized[key] = val

    return signed_sortings_normalized.keys()


def normalize_city_input(input):
    data = {
        "name": input.name if input.name != UNSET else None,
        "country": input.country if input.country != UNSET else None,
        "region": input.region if input.region != UNSET else None,
        "timezone": input.timezone if input.timezone != UNSET else None,
        "latitude": input.latitude if input.latitude != UNSET else None,
        "longitude": input.longitude if input.longitude != UNSET else None,
    }

    # Filter out data that's None
    normalized_data = {}
    for key, val in data.items():
        if val is not None:
            normalized_data[key] = val

    return normalized_data
