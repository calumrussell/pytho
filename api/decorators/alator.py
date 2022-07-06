# type: ignore
from functools import wraps
import json

from django.http.request import HttpRequest

from helpers.alator import AlatorClientInput
from helpers.response import ErrorResponse


def alator_input():
    """
    Throws error if inputs are malformed.
    """

    def decorator(func):
        @wraps(func)
        def inner(request: HttpRequest, *args, **kwargs):

            req_body = json.loads(request.body.decode("utf-8"))
            if "data" not in req_body:
                return ErrorResponse.create(
                    400, "Client passed no data to run backtest on"
                )

            body_data = req_body.get("data")
            if "assets" not in body_data:
                return ErrorResponse.create(
                    400, "Client passed no data to run backtest on"
                )
            if "weights" not in body_data:
                return ErrorResponse.create(
                    400, "Client passed no data to run backtest on"
                )

            assets = body_data.get("assets")
            weights = body_data.get("weights")

            if len(assets) != len(weights):
                return ErrorResponse.create(400, "Input data is invalid")

            if not assets or not weights:
                return ErrorResponse.create(400, "Input data is invalid")

            alator = AlatorClientInput(assets=assets, weights=weights)
            return func(request, alator=alator, *args, **kwargs)

        return inner

    return decorator
