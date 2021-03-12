class ApiResponse:
    """
    Default api response object class to be used by services
    """
    def __init__(self, message=None):
        """
        Response constructor with defaults
        :param message: Optional init message for the response
        """
        self.success = False
        self.message = message
        self.data = None

    def update(self, success: bool, message: str, data=None):
        """
        Method to update success status, response message and data
        :param success: Boolean for response success status
        :param message: Message to be sent with the response
        :param data: Data to be sent with the response
        """
        self.success = success
        self.message = message
        self.data = data

    def json(self):
        """
        Method to return response in serialized dict form
        """
        obj = {"success": self.success, "message": self.message, "data": self.data}
        return obj
