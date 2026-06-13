# Input Errors
class InputError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.name = "InputError"
        self.status_code = 400

# Access Errors
class AccessError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.name = "AccessError"
        self.status_code = 403