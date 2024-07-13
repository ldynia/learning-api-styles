from typing import List
from typing import Tuple
from uuid import UUID

from .validators import Validator
from config.constants import OM_API_DATE_END
from config.constants import OM_API_DATE_START
from config.constants import OM_API_YEAR_END
from config.constants import OM_API_YEAR_START


class InputDataValidator(Validator):
    """
    A class containing methods to validate input data based on various criteria.

    Args:
        Validator: The base class containing common validation methods.
    """

    def __init__(self, param: str):
        self.errors = []
        self.param = param

    def valid_uuid(self, value: UUID) -> Tuple[bool, List[str]]:
        """
        Validate UUID value.

        Args:
            value (UUID): The list of UUID values to be validated.

        Returns:
            Tuple[bool, List[str]]: A tuple indicating validation success and a list of error messages.
        """
        if not super().valid_uuid(value):
            self.errors.append(f"Parameter `{self.param}` value `{value}` is invalid UUID.")

        return not self.errors, self.errors

    def valid_city_lat_lon(self, city: str, lat: str, lon: str) -> Tuple[bool, List[str]]:
        """
        Validate city, latitude, and longitude values.

        Args:
            city (str): The city value to be validated.
            lat (str): The latitude value to be validated.
            lon (str): The longitude value to be validated.

        Returns:
            Tuple[bool, List[str]]: A tuple indicating validation success and a list of error messages.
        """
        valid_values = ((city != "" or city) or ((lat != "" or lat) and (lon != "" or lon)))
        if not valid_values:
            self.errors.append("Parameter `city` OR `lat` and `lon` cannot be empty.")

        # Validate lat and lon if city is not set
        if city == "" or not city:
            valid_floats = (lat and lon) and ((self.valid_float(lat) and self.valid_float(lon)))
            if not valid_floats:
                self.errors.append("Parameter `lat` and `lon` is invalid or missing.")

        # Validate city if set
        if city != "" and city:
            if not self.valid_str(city):
                self.errors.append(f"Parameter `city` is type of `{type(city)}` expected type is `str'.")

            if not self.valid_min_length(city):
                self.errors.append("Parameter `city` cannot be empty str.")

        return not self.errors, self.errors

    def valid_dates(self, start_date: str, end_date: str) -> Tuple[bool, List[str]]:
        """
        Validate start and end date values.

        Args:
            start_date (str): The start date value to be validated.
            end_date (str): The end date value to be validated.

        Returns:
            Tuple[bool, List[str]]: A tuple indicating validation success and a list of error messages.
        """
        valid_start_date = type(start_date) == str and start_date != ""
        if not valid_start_date:
            self.errors.append("Parameter `start_date` cannot be empty.")

        valid_end_date = type(end_date) == str and end_date != ""
        if not valid_end_date:
            self.errors.append("Parameter `end_date` cannot be empty.")

        date_format = "%Y-%m-%d"
        if not self.valid_date(start_date, fmt=date_format):
            self.errors.append(f"Parameter `start_date` {start_date} has invalid format. Allowed format is {date_format}.")

        if not self.valid_date(end_date, fmt=date_format):
            self.errors.append(f"Parameter `end_date` {end_date} has invalid format. Allowed format is {date_format}.")

        if start_date != "" and end_date != "":
            if not self.valid_date_points(start_date, end_date):
                self.errors.append(f"Parameter start_date `{start_date}` cannot be grater than end_date {end_date}.")

            if not self.valid_date_range(start_date, end_date, OM_API_DATE_START, OM_API_DATE_END):
                self.errors.append(
                    "Parameter `start_date` or `end_date` is in invalid range." +
                    f"Allowed range is starts at {OM_API_DATE_START} ends at {OM_API_DATE_END}."
                )

        return not self.errors, self.errors

    def valid_day(self, value: str | int, min_val: int, max_val: int) -> Tuple[bool, List[str]]:
        """
        Validate a day value within a specified range.

        Args:
            value (str | int): The day value to be validated.
            min_val (int): The minimum allowed value.
            max_val (int): The maximum allowed value.

        Returns:
            Tuple[bool, List[str]]: A tuple indicating validation success and a list of error messages.
        """
        valid_values = ((isinstance(value, str) and value != "") or (value is not None))
        if not valid_values:
            self.errors.append(f"Parameter `{self.param}` cannot be empty.")

        if not self.valid_int(value):
            self.errors.append(f"Parameter `{self.param}` is type of `{type(value)}` expected type is `int'.")

        if not self.valid_range(value, min_val, max_val):
            self.errors.append(f"Parameter `{self.param}` ({value}) is in invalid range. Allowed range is {min}-{max}.")

        return not self.errors, self.errors

    def valid_fields(self, value: str, allowed_fields: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate a string field value.

        Args:
            value (str): The field value to be validated.
            allowed_fields (List[str]): A list of allowed field values.

        Returns:
            Tuple[bool, List[str]]: A tuple indicating validation success and a list of error messages.
        """
        if not self.valid_str(value):
            self.errors.append(f"Parameter `{self.param}` is type of `{type(value)}` expected type is `str'.")

        if not self.valid_min_length(value):
            self.errors.append(f"Parameter `{self.param}` cannot be empty str.")

        for field in value.split(","):
            if field not in allowed_fields:
                self.errors.append(f"Field `{field}` in parameter `{self.param}` is not allowed.")

        return not self.errors, self.errors

    def valid_sort(self, value: str, allowed_fields: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate a string field value.

        Args:
            value (str): The field value to be validated.
            allowed_fields (List[str]): A list of allowed field values.

        Returns:
            Tuple[bool, List[str]]: A tuple indicating validation success and a list of error messages.
        """
        if not self.valid_str(value):
            self.errors.append(f"Parameter `{self.param}` is type of `{type(value)}` expected type is `str'.")

        if not self.valid_min_length(value):
            self.errors.append(f"Parameter `{self.param}` cannot be empty str.")

        if value not in allowed_fields:
            self.errors.append(f"Value `{value}` in parameter `{self.param}` is not allowed.")

        return not self.errors, self.errors

    def valid_year(self, value: int) -> Tuple[bool, List[str]]:
        """
        Validate a year value.

        Args:
            value (int): The year value to be validated.

        Returns:
            Tuple[bool, List[str]]: A tuple indicating validation success and a list of error messages.
        """
        if not self.valid_range(value, OM_API_YEAR_START, OM_API_YEAR_END):
            self.errors.append(
                f"Parameter `{self.param}` {value} has invalid range. " +
                f"Allowed range is {OM_API_YEAR_START}-{OM_API_YEAR_END}."
            )

        return not self.errors, self.errors
