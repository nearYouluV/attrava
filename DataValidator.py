import re


class DataValidator:
    """
    Class for validating data received from the API.
    """

    @staticmethod
    def validate_email(data: dict) -> bool:
        """
        Validates an email address.

        :param email: The email address to validate.
        :return: True if valid, False otherwise.
        """
        email = data.get("Email")

        if not isinstance(email, str):
            return False
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return bool(re.match(email_regex, email))

    @staticmethod
    def validate_phone(data: dict) -> bool:
        """
        Validates a phone number (supports various international formats including dots, spaces, and dashes).

        :param phone: The phone number to validate.
        :return: True if valid, False otherwise.
        """

        phone = data.get("Phone")
        if not isinstance(phone, str):
            return False
        phone_regex = r"^\+?[1-9]\d{0,2}[\s.-]?\(?\d{1,4}\)?[\s.-]?\d{1,4}[\s.-]?\d{1,4}[\s.-]?\d{1,4}$"
        return bool(re.match(phone_regex, phone))
