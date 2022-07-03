from tokenize import String
from typing import Dict, List, Any
from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
import json

from api.models import Coverage
from helpers import analysis, prices
from helpers.analysis.drawdown import HistoricalDrawdownEstimatorResult
from helpers.analysis.riskattribution import (
    BootstrapRiskAttributionResult,
    RiskAttributionResult,
    RollingRegressionInput,
    RollingRiskAttributionResult,
)
from api.decorators import (  # type: ignore
    regression_input,
    alator_input,
    antevorta_input,
)
from helpers.alator import (
    FixedSignalBackTestWithPriceAPI,
    AlatorUnusableInputException,
    AlatorClientInput,
)
from helpers.antevorta import (
    DefaultSimulationWithPriceAPI,
    AntevortaUnusableInputException,
    AntevortaClientInput,
)
from helpers.prices.data import DataSource
from helpers.response import ErrorResponse


@csrf_exempt  # type: ignore
@require_POST  # type: ignore
@antevorta_input()
def antevorta_simulation(
    request: HttpRequest, antevorta: AntevortaClientInput
) -> JsonResponse:
    """
    Parameters
    --------
    data : `Dict[assets : List[int], weights : List[float]], initial_cash: float, wage: float, income_growth: float`
      Assets and weights to run static benchmark against

    Returns
    --------
    200
      Income simulation runs successfully and returns performance numbers
    400
      Client passes an input that is does not have any required parameters
    404
      Client passes a valid input but these can't be used to run a backtest
    405
      Client attempts a method other than POST
    503
      Couldn't connect to downstream API
    """
    try:
        inc = DefaultSimulationWithPriceAPI(antevorta)
        inc.run()
        return JsonResponse({"data": dict(inc.results)}, status=200)
    except AntevortaUnusableInputException:
        return ErrorResponse.create(404, "Backtest could not run with inputs")
    except ConnectionError:
        return ErrorResopnse.create(503, "Couldn't complete simulation")


@csrf_exempt  # type: ignore
@require_POST  # type: ignore
@alator_input()
def alator_backtest(request: HttpRequest, alator: AlatorClientInput) -> JsonResponse:
    """
    Parameters
    --------
    data : `Dict[assets : List[int], weights : List[float]]`
      Assets and weights to run static benchmark against

    Returns
    --------
    200
      Backtest runs successfully and returns performance numbers
    400
      Client passes an input that is does not have any required parameters
    404
      Client passes a valid input but these can't be used to run a backtest
    405
      Client attempts a method other than POST
    503
      Couldn't connect to downstream API
    """
    try:
        bt: FixedSignalBackTestWithPriceAPI = FixedSignalBackTestWithPriceAPI(alator)
        bt.run()
        return JsonResponse({"data": dict(bt.results)}, status=200)
    except AlatorUnusableInputException:
        return ErrorResponse.create(404, "Backtest could not run with inputs")
    except ConnectionError:
        return ErrorResponse.create(503, "Couldn't complete backtest")


@regression_input(has_window=True)  # type: ignore
@require_GET  # type: ignore
def risk_attribution(
    request: HttpRequest, regression: RollingRegressionInput, coverage: List[Coverage]
) -> JsonResponse:
    """
    Parameters
    --------
    request: `HttpRequest`
    regression: `RollingRegressionInput`
    coverage: `List[Coverage]`

    Returns
    --------
    200
      Risk attribution runs and returns estimate
    400
      Client passes an input that is does not have any required parameters
    404
      Client passes a valid input but these can't be used to run a backtest
    405
      Client attempts a method other than GET
    503
      Couldn't connect to downstream API
    """
    req: prices.PriceAPIRequestsMonthly = prices.PriceAPIRequestsMonthly(coverage)
    model_prices: Dict[int, DataSource] = req.get()

    try:
        rra: analysis.RollingRiskAttribution = analysis.RollingRiskAttribution(
            roll_input=regression,
            data=model_prices,
        )
        rra_res: RollingRiskAttributionResult = rra.run()

        ra: analysis.RiskAttribution = analysis.RiskAttribution(
            reg_input=regression, data=model_prices
        )
        ra_res: RiskAttributionResult = ra.run()

        bra: analysis.BootstrapRiskAttributionAlt = (
            analysis.BootstrapRiskAttributionAlt(
                reg_input=regression,
                data=model_prices,
            )
        )
        bra_res: BootstrapRiskAttributionResult = bra.run()

        res: Dict[String, Any] = {
            "core": ra_res,
            "rolling": rra_res,
            "bootstrap": bra_res,
        }
        return JsonResponse(res, safe=False)
    except analysis.RiskAttributionUnusableInputException as e:
        return JsonResponse({"status": "false", "message": str(e.message)}, status=404)
    except analysis.WindowLengthError:
        return JsonResponse(
            {"status": "false", "message": "Window length invalid"}, status=400
        )
    except ConnectionError:
        return JsonResponse(
            {
                "status": "false",
                "message": "Couldn't complete request due to connection error",
            },
            status=503,
        )


@regression_input(has_window=False)  # type: ignore
@require_GET  # type: ignore
def hypothetical_drawdown_simulation(
    request: HttpRequest, regression: RollingRegressionInput, coverage: List[Coverage]
) -> JsonResponse:
    """
    Parameters
    --------
    request: `HttpRequest`
    regression: `RollingRegressionInput`
    coverage: `List[Coverage]`

    Returns
    --------
    200
      Risk attribution runs and returns estimate
    400
      Client passes an input that is does not have any required parameters
    404
      Client passes a valid input but these can't be used to run a backtest
    405
      Client attempts a method other than GET
    503
      Couldn't connect to downstream API
    """
    req: prices.PriceAPIRequestsMonthly = prices.PriceAPIRequestsMonthly(coverage)
    model_prices: Dict[int, DataSource] = req.get()

    try:
        hde: analysis.HistoricalDrawdownEstimatorFromDataSources = (
            analysis.HistoricalDrawdownEstimatorFromDataSources(
                reg_input=regression, model_prices=model_prices, threshold=-0.1
            )
        )
        res: HistoricalDrawdownEstimatorResult = hde.get_results()
        return JsonResponse(res)
    except analysis.RiskAttributionUnusableInputException as e:
        return JsonResponse({"status": "false", "message": str(e.message)}, status=404)
    except analysis.HistoricalDrawdownEstimatorNoFactorSourceException:
        return JsonResponse(
            {"status": "false", "message": "Independent variables must be factor"},
            status=400,
        )
    except ConnectionError:
        return JsonResponse(
            {
                "status": "false",
                "message": "Couldn't complete request due to connection error",
            },
            status=503,
        )


@require_GET  # type: ignore
def price_coverage_suggest(request: HttpRequest) -> JsonResponse:
    security_type: str = request.GET.get("security_type", None)
    if not security_type:
        return JsonResponse(
            {"status": "false", "message": "security_type is required parameter"},
            status=400,
        )

    suggest_str: str = request.GET.get("s", None).lower()
    if not suggest_str:
        return JsonResponse(
            {"status": "false", "message": "s is required parameter"}, status=400
        )

    if len(suggest_str) < 2:
        ##We return empty whenever string isn't long enough to return good results
        return JsonResponse({"coverage": []}, status=200)

    return JsonResponse(
        {
            "coverage": list(
                Coverage.objects.filter(
                    security_type=security_type,
                    name__icontains=suggest_str,
                ).values()
            )
        },
        status=200,
    )
