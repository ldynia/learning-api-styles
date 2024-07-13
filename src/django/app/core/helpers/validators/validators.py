from datetime import datetime
from typing import Any
from uuid import UUID


class Validator:
    """
    A collection of utility methods for validating various types of data.
    """

    def valid_uuid(self, value: str, version: int = 4) -> bool:
        """
        Validate if the given value is a valid UUID.

        Args:
            value (str): The value to validate as a UUID.
            version (int, optional): The UUID version. Defaults to 4.

        Returns:
            bool: True if the value is a valid UUID, False otherwise.
        """
        try:
            UUID(str(value), version=version)
            return True
        except ValueError:
            return False

    def valid_min_length(self, value: str, length: int = 1) -> bool:
        """
        Validate if the length of the given value is greater than or equal to a specified minimum length.

        Args:
            value (str): The value to validate.
            length (int, optional): The minimum length. Defaults to 1.

        Returns:
            bool: True if the length is valid, False otherwise.
        """
        try:
            return len(value) >= length
        except ValueError:
            return False

    def valid_range(self, value: int | str, min_value: int, max_value: int) -> bool:
        """
        Validate if the given value is within a specified range.

        Args:
            value (int or str): The value to validate.
            min_value (int): The minimum allowed value.
            max_value (int): The maximum allowed value.

        Returns:
            bool: True if the value is within the range, False otherwise.
        """
        try:
            return min_value <= int(value) <= max_value
        except ValueError:
            return False

    def valid_int(self, value: int | str) -> bool:
        """
        Validate if the given value is a valid integer.

        Args:
            value (int or str): The value to validate.

        Returns:
            bool: True if the value is a valid integer, False otherwise.
        """
        return isinstance(value, int) or value.isdigit()

    def valid_str(self, value: Any) -> bool:
        """
        Validate if the given value is a string.

        Args:
            value (Any): The value to validate.

        Returns:
            bool: True if the value is a string, False otherwise.
        """
        return isinstance(value, str)

    def valid_float(self, value: str) -> bool:
        """
        Validate if the given string can be converted to a float.

        Args:
            value (str): The string to be validated as a float.

        Returns:
            bool: True if the value can be converted to a float, False otherwise.
        """
        try:
            float(value)
            return True
        except ValueError:
            return False

    def contains_char(self, value: str, char: str) -> bool:
        """
        Check if the given character exists in the given string.

        Args:
            value (str): The string to be checked.
            char (str): The character to check for.

        Returns:
            bool: True if the character exists in the string, False otherwise.
        """
        return char in value

    def valid_date(self, date: str, fmt: str = "%Y-%m-%d") -> bool:
        """
        Validate if the given string is a valid date in the specified format.

        Args:
            date (str): The string to be validated as a date.
            fmt (str, optional): The date format to validate against. Default is "%Y-%m-%d".

        Returns:
            bool: True if the value is a valid date in the specified format, False otherwise.
        """
        try:
            return bool(datetime.strptime(date, fmt))
        except ValueError:
            return False

    def valid_date_points(self, start_date: str, end_date: str, fmt: str = "%Y-%m-%d") -> bool:
        """
        Validate if the given start and end dates form a valid date range.

        Args:
            start_date (str): The start date string.
            end_date (str): The end date string.
            fmt (str, optional): The date format to validate against. Default is "%Y-%m-%d".

        Returns:
            bool: True if the start and end dates form a valid date range, False otherwise.
        """
        try:
            start_date = datetime.strptime(start_date, fmt)
            end_date = datetime.strptime(end_date, fmt)
            return start_date <= end_date
        except ValueError:
            return False

    def valid_date_range(self, start_date: str, end_date: str, start_date_range: str,
                         end_date_range: str, fmt: str = "%Y-%m-%d") -> bool:
        """
        Validate if the given date range is within the specified valid date range.

        Args:
            start_date (str): The start date string to be validated.
            end_date (str): The end date string to be validated.
            start_date_range (str): The start of the valid date range to compare against.
            end_date_range (str): The end of the valid date range to compare against.
            fmt (str, optional): The date format to validate against. Default is `%Y-%m-%d`.

        Returns:
            bool: True if the given date range is within the specified valid date range, False otherwise.
        """
        try:
            start_date = datetime.strptime(start_date, fmt)
            end_date = datetime.strptime(end_date, fmt)
            start_date_range = datetime.strptime(start_date_range, fmt)
            end_date_range = datetime.strptime(end_date_range, fmt)
            return start_date >= start_date_range and end_date <= end_date_range
        except ValueError:
            return False
