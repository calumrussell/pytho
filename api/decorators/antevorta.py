# type: ignore
from functools import wraps
import json

from django.http.request import HttpRequest

from helpers.antevorta import AntevortaClientInput
from helpers.response import ErrorResponse


def antevorta_input():
    """
    Throws error if inputs are malformed.
    """

    def decorator(func):
        @wraps(func)
        def inner(request: HttpRequest, *args, **kwargs):

            req_body = json.loads(request.body.decode("utf-8"))
            if "data" not in req_body:
                return ErrorResponse.create(
                    400, "Client passed no data to run simulation on"
                )

            body_data = req_body.get("data")
            if "assets" not in body_data:
                return ErrorResponse.create(
                    400, "Client passed no data to run simulation on"
                )
            if "weights" not in body_data:
                return ErrorResponse.create(
                    400, "Client passed no data to run simulation on"
                )
            if "initial_cash" not in body_data:
                return ErrorResponse.create(
                    400, "Client passed no data to run simulation on"
                )
            if "wage" not in body_data:
                return ErrorResponse.create(
                    400, "Client passed no data to run simulation on"
                )
            if "wage_growth" not in body_data:
                return ErrorResponse.create(
                    400, "Client passed no data to run simulation on"
                )
            if "contribution_pct" not in body_data:
                return ErrorResponse.create(
                    400, "Client passed no data to run simulation on"
                )
            if "emergency_cash_min" not in body_data:
                return ErrorResponse.create(
                    400, "Client passed no data to run simulation on"
                )
            if "sim_length" not in body_data:
                return ErrorResponse.create(
                    400, "Client passed no data to run simulation on"
                )

            assets = body_data.get("assets")
            weights = body_data.get("weights")

            if len(assets) != len(weights):
                return ErrorResponse.create(400, "Input data is invalid")

            if not assets or not weights:
                return ErrorResponse.create(400, "Input data is invalid")

            initial_cash = body_data.get("initial_cash")
            wage = body_data.get("wage")
            wage_growth = body_data.get("wage_growth")
            contribution_pct = body_data.get("contribution_pct")
            emergency_cash_min = body_data.get("emergency_cash_min")
            sim_length = body_data.get("sim_length")

            if (
                initial_cash < 0
                or wage < 0
                or wage_growth < 0
                or contribution_pct < 0
                or emergency_cash_min < 0
                or sim_length < 0
            ):
                return ErrorResponse.create(400, "Input data is invalid")

            antevorta = AntevortaClientInput(
                assets=assets,
                weights=weights,
                initial_cash=initial_cash,
                wage=wage,
                wage_growth=wage_growth,
                contribution_pct=contribution_pct,
                emergency_cash_min=emergency_cash_min,
                sim_length=sim_length,
            )
            return func(request, antevorta=antevorta, *args, **kwargs)

        return inner

    return decorator
