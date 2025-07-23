import requests


# Definicion de la clase respuesta de los request en los test
class MockResponse:
    def __init__(self, data, status_code=200, raise_http=False, is_json=True):
        self._data = data
        self.status_code = status_code
        self.raise_http = raise_http
        self.is_json = is_json

    # metodo response.json para ver la data del response
    def json(self):
        if not self.is_json:
            raise ValueError("Invalid JSON")
        return self._data

    # metodo para lanzar un error HTTP
    def raise_for_status(self):
        if self.raise_http:
            raise requests.exceptions.HTTPError("Mock HTTP error")
