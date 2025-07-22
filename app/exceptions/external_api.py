class ExternalAPIError(Exception):
    def __init__(self, message, status_code=None, payload=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code or 502
        self.payload = payload or {}

    def to_dict(self):
        di = dict(self.payload)
        di["error"] = self.message
        return di
