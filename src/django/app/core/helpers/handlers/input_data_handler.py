import re

from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import Dict
from typing import List
from typing import Set
from typing import Tuple
from urllib.parse import unquote_plus

from rest_framework.request import Request

from config.constants import APP_DEFAULT_YEAR


class InputDataHandler:

    def __init__(self, validator, query=True, request=True):
        """
        Initialize the InputDataHandler.

        Args:
            validator: An instance of the validator class.
            query (bool): Indicates whether data should be retrieved from query parameters.
            request (bool): Indicates whether data should be retrieved from the request body.
        """
        self.validator = validator
        self.from_query = query
        self.from_request = request

    def handle_city_uuid(self, input: Dict[str, Any] | Request) -> Tuple[List[str], str | None]:
        """
        Handle UUID list data from the request.

        Args:
            input (dict|Request): The request object.

        Returns:
            Tuple[List[str], str | None]: A tuple containing errors and UUID if valid, otherwise None.
        """
        if not self.from_request:
            uid = input.city_uuid

        if self.from_request and self.from_query:
            uid = input.query_params.get("city_uuid", None)

        if self.from_request and not self.from_query:
            uid = input.data.get("city_uuid", None)

        if not uid:
            return None, []

        valid, errors = self.validator("city_uuid").valid_uuid(uid)
        if not valid:
            return None, errors

        return uid, errors

    def valid_city_lat_lon(self, input: Dict[str, Any] | Request) -> Tuple[List[str], Tuple[str, str, str] | None]:
        """
        Validate and handle city, latitude, and longitude data from the request.

        Args:
            input (dict(str,any) | Request): The input data.

        Returns:
            Tuple[List[str], Tuple[str, str, str] | None ]: A tuple containing errors and data if valid, otherwise None.
        """
        if not self.from_request:
            city = input.city
            lat = input.latitude
            lon = input.longitude

        if self.from_request and self.from_query:
            city = input.query_params.get("city", "")
            lat = input.query_params.get("lat", "")
            lon = input.query_params.get("lon", "")

        if self.from_request and not self.from_query:
            city = input.data.get("city", "")
            lat = input.data.get("lat", "")
            lon = input.data.get("lon", "")

        valid, errors = self.validator("city_lat_lon").valid_city_lat_lon(city, lat, lon)
        if not valid:
            return None, errors

        return (city, lat, lon), []

    def handle_dates(self, request: Request) -> Tuple[List[str], Tuple[datetime, datetime] | None]:
        """
        Handle start and end dates from the request.

        Args:
            request (Request): The request object.

        Returns:
            Tuple[List[str], Tuple[datetime, datetime] | None]: A tuple containing errors and dates if valid, otherwise None.
        """
        if self.from_query:
            start_date = request.query_params.get("start_date", "")
            end_date = request.query_params.get("end_date", "")
        else:
            start_date = request.data.get("start_date", "")
            end_date = request.data.get("end_date", "")

        if start_date == "" and end_date == "":
            start_date = datetime.now().date() - timedelta(days=7)
            end_date = datetime.now().date()
            return (start_date, end_date), []

        valid, errors = self.validator("dates").valid_dates(start_date, end_date)
        if not valid:
            return None, errors

        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        return (start_date, end_date), errors

    def handle_days(self, request: Request | int) -> Tuple[List[str], int]:
        """
        Handle the number of days from the request.

        Args:
            request (Request): The request object.

        Returns:
            Tuple[List[str], int]: A tuple containing errors and the number of days if valid, otherwise None.
        """
        # check if instance of request
        if isinstance(request, int):
            days = request
        else:
            if not self.from_request:
                days = request.days

            if not self.from_request:
                days = request.days

            if self.from_request and self.from_query:
                days = request.query_params.get("days", 7)

            if self.from_request and not self.from_query:
                days = request.data.get("days", 7)

        valid, errors = self.validator("days").valid_day(days, 1, 7)
        if not valid:
            return 7, errors

        return int(days), []

    def handle_fields(self, request: Request, allowed_values: List[str]) -> Tuple[List[str], Set[str] | None]:
        """
        Handle the list of fields from the request.

        Args:
            request (Request): The request object.
            allowed_values (List[str]): A list of allowed fields.

        Returns:
            Tuple[List[str], Set[str] | None]: A tuple containing errors and values if valid, otherwise None.
        """
        if self.from_query:
            fields = request.query_params.get("fields", None)
        else:
            fields = request.data.get("fields", None)

        if fields:
            valid, errors = self.validator("fields").valid_fields(fields, allowed_values)
            if not valid:
                return None, errors

            return set(fields.split(",")), []

        return None, []

    def handle_sort(self, request: Request, allowed_values: List[str]) -> Tuple[List[str], Set[str] | None]:
        """
        Handle the list of fields from the request.
        Regex check if sorting values matches 'word' or '-word'.

        Args:
            request: The request object.
            allowed_values: A list of allowed values.

        Returns:
            Tuple[List[str], Set[str] | None]: A tuple containing errors and values if valid, otherwise None.
        """
        sort = request.query_params.get("sort", "name")
        if not re.match(r"^(\w+|-\w+)$", sort):
            return None, [f"Value '{sort}' in parameter 'sort' is not allowed."]

        sort_key = re.findall(r"\w+", sort)[0]
        valid, errors = self.validator("sort").valid_sort(sort_key, allowed_values)
        if not valid:
            return None, errors

        # Check if first character is a letter then normalize
        return sort_key if re.match(r'^[a-zA-Z]', sort) else f"-{sort_key}", []

    def handle_search(self, request: Request, allowed_values: List[str], prefix="search_") -> Tuple[List[str], Dict[str, Any] | None]:
        """
        Handle the list of fields from the request.

        Args:
            request (Request): The request object.
            allowed_values (List[str]): A list of allowed values.

        Returns:
            Tuple[List[str], Set[str] | None]: A tuple containing errors and values if valid, otherwise None.
        """
        query_params = request.query_params.urlencode()
        if prefix not in query_params:
            return dict(), []

        search_regex = r"(search_[^=]+)=([^&]*)"
        matches = re.findall(search_regex, query_params)
        if not matches:
            return None, [f"Query parameter '{prefix}' is missing search key."]

        first_search_match = matches[0]
        search_key, search_value = first_search_match[0].replace(prefix, ""), unquote_plus(first_search_match[1])

        if search_value == "":
            return None, [f"Query parameter '{prefix}{search_key}' is missing value."]

        if search_key and search_value:
            if search_key not in allowed_values:
                return None, [f"Key '{search_key}' is not searchable"]

            # handle number values
            try:
                if search_value.isdigit():
                    return {search_key: int(search_value)}, []
                return {search_key: float(search_value)}, []
            except Exception:
                return {f"{search_key}__icontains": search_value}, []

        return dict(), []

    def handle_year(self, input: Dict[str, Any] | Request) -> Tuple[List[str], int | None]:
        """
        Handle the year from the request.

        Args:
            input (dict|request): The request object.
            value (int): Year to validate defaults to APP_DEFAULT_YEAR

        Returns:
            Tuple[List[str], int]: A tuple containing errors and the year if valid, otherwise None.
        """
        if not self.from_request:
            year = input.year

        if self.from_request and self.from_query:
            year = input.query_params.get("year", APP_DEFAULT_YEAR)

        if self.from_request and not self.from_query:
            year = input.data.get("year", APP_DEFAULT_YEAR)

        valid, errors = self.validator("year").valid_year(year)
        if not valid:
            return None, errors

        return int(year), []
