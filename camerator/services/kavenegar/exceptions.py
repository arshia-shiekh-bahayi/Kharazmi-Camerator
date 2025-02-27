class MobileNumberException(Exception):
    def __init__(self, message: str = "The mobile number is invalid."):
        super().__init__(message)


class KavenegarRequestException(Exception):
    def __init__(self, message: str = "There is a server error."):
        super().__init__(message)
