import json

from braintreehttp import HttpClient
from braintreehttp import Injector
from access_token_request import AccessTokenRequest
from access_token import AccessToken


class PayPalHttpClient(HttpClient, Injector):

    def __init__(self, environment, refresh_token=None):
        HttpClient.__init__(self, environment)
        self._refresh_token = refresh_token
        self._access_token = None
        self.environment = environment

        self.add_injector(injector=self)

    def serialize_request(self, request):
        if self.content_type(request.headers) == "application/json":
            return json.dumps(request.request_body)

        raise IOError("Unable to serialize content {0} with Content-Type: {1}".format(request.request_body, self.content_type(request.headers)))

    def deserialize_response(self, response_body, headers):
        if self.content_type(headers) == "application/json":
            return json.loads(response_body)

        raise IOError("Unsupported Content-Type: {0}".format(self.content_type(headers)))

    def __call__(self, request):
        if "Accept-Encoding" not in request.headers:
            request.headers["Accept-Encoding"] = "gzip"

        if not isinstance(request, AccessTokenRequest):
            if not self._access_token or self._access_token.is_expired():
                accesstokenresult = self.execute(AccessTokenRequest(self.environment, self._refresh_token)).result
                self._access_token = AccessToken(access_token=accesstokenresult.access_token,
                                                 expires_in=accesstokenresult.expires_in,
                                                 token_type=accesstokenresult.token_type)

            request.headers["Authorization"] = self._access_token.authorization_string()

    @staticmethod
    def content_type(headers):
        if "Content-Type" in headers:
            return headers["Content-Type"]

        return None