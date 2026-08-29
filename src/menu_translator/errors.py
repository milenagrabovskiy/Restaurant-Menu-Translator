class RestaurantManagementError(Exception):
    """Base custom exception for the application. Handled by errorhandler()"""

    def __init__(self, code: str, status: int, detail: str | None):
        super().__init__(detail or code)
        self.code = code
        self.status = status
        self.detail = detail


class AWSError(Exception):
    """Customer error for errors related to AWS"""
