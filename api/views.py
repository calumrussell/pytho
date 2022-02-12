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
    RollingRiskAttributionResult,
)
from helpers.prices.api import HermesAPI
from api.decorators import (  # type: ignore
    regression_input_parse,
    RollingRegressionInput,
)
from helpers.backtest import (
    FixedSignalBackTestWithPriceAPI,
    BackTestUnusableInputException,
    BackTestInvalidInputException,
)
from helpers.prices.data import (
    DataSource,
    HermesDailyResponse,
    HermesEarningsSource,
    HermesFundamentalResponse,
    HermesFundamentalSource,
    HermesPeriod,
    HermesPriceSource,
)


@csrf_exempt  # type: ignore
@require_POST  # type: ignore
def backtest_portfolio(request: HttpRequest) -> JsonResponse:
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
    req_body: Dict[str, Any] = json.loads(request.body.decode("utf-8"))
    if "data" not in req_body:
        return JsonResponse(
            {"status": "false", "message": "Client passed no data to run backtest on"},
            status=400,
        )

    bt_portfolio: Dict[str, List[Any]] = req_body["data"]
    resp: Dict[str, Dict[str, Any]] = {}
    resp["data"] = {}

    assets: List[int] = bt_portfolio["assets"]
    weights: List[float] = bt_portfolio["weights"]

    try:
        bt: FixedSignalBackTestWithPriceAPI = FixedSignalBackTestWithPriceAPI(
            assets, weights
        )
        bt.run()
    except BackTestInvalidInputException:
        return JsonResponse(
            {"status": "false", "message": "Inputs are invalid"}, status=404
        )
    except BackTestUnusableInputException:
        return JsonResponse(
            {"status": "false", "message": "Backtest could not run with inputs"},
            status=404,
        )
    except ConnectionError:
        return JsonResponse(
            {
                "status": "false",
                "message": "Couldn't complete request due to connection error",
            },
            status=503,
        )
    else:
        ##mypy doesn't know runtime identity of TypedDict
        resp["data"] = dict(bt.results)
        return JsonResponse(resp, status=200)


@regression_input_parse(has_window=True)  # type: ignore
@require_GET  # type: ignore
def risk_attribution(
    request: HttpRequest, regression: RollingRegressionInput, coverage: List[Coverage]
) -> JsonResponse:
    """
    Parameters
    --------
    ind : `List[int]`
      List of independent variable asset ids for regression
    dep : int
      Asset id for dependent variable in regression

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
    dep = regression["dep"]
    ind = regression["ind"]
    window = regression["window"]

    req: prices.PriceAPIRequestsMonthly = prices.PriceAPIRequestsMonthly(coverage)
    model_prices: Dict[int, DataSource] = req.get()

    try:
        rra: analysis.RollingRiskAttribution = analysis.RollingRiskAttribution(
            dep=dep,
            ind=ind,
            data=model_prices,
            window_length=window,
        )
        rra_res: RollingRiskAttributionResult = rra.run()

        ra: analysis.RiskAttribution = analysis.RiskAttribution(
            dep=dep, ind=ind, data=model_prices
        )
        ra_res: RiskAttributionResult = ra.run()

        bra: analysis.BootstrapRiskAttributionAlt = (
            analysis.BootstrapRiskAttributionAlt(
                dep=dep,
                ind=ind,
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


@regression_input_parse(has_window=False)  # type: ignore
@require_GET  # type: ignore
def hypothetical_drawdown_simulation(
    request: HttpRequest, regression: RollingRegressionInput, coverage: List[Coverage]
) -> JsonResponse:
    """
    Parameters
    --------
    ind : `List[int]`
      List of independent variable asset ids for regression
    dep : int
      Asset id for dependent variable in regression

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
    ind = regression["ind"]
    dep = regression["dep"]

    req: prices.PriceAPIRequestsMonthly = prices.PriceAPIRequestsMonthly(coverage)
    model_prices: Dict[int, DataSource] = req.get()

    try:
        hde: analysis.HistoricalDrawdownEstimatorFromDataSources = (
            analysis.HistoricalDrawdownEstimatorFromDataSources(
                ind=ind, dep=dep, model_prices=model_prices, threshold=-0.1
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
def hermes_daily_price(request: HttpRequest) -> JsonResponse:
    ticker: str = request.GET.get("ticker", None)
    if not ticker:
        raise JsonResponse(
            {"status": "false", "message": "ticker is required parameter"},
            status=400,
        )

    res: list = HermesAPI.get_daily_price(ticker)
    resp: HermesDailyResponse = HermesPriceSource(res, HermesPeriod.DAILY).get()
    return JsonResponse(resp, status=200)


@require_GET  # type: ignore
def hermes_fundamentals(request: HttpRequest) -> JsonResponse:
    ticker: str = request.GET.get("ticker", None)
    if not ticker:
        raise JsonResponse(
            {"status": "false", "message": "ticker is required parameter"},
            status=400,
        )

    res: dict = HermesAPI.get_fundamentals(ticker)
    resp: HermesFundamentalResponse = HermesFundamentalSource(
        res, HermesPeriod.YEARLY
    ).get()
    return JsonResponse(resp, status=200)


@require_GET  # type: ignore
def hermes_earnings(request: HttpRequest) -> JsonResponse:
    ticker: str = request.GET.get("ticker", None)
    if not ticker:
        raise JsonResponse(
            {"status": "false", "message": "ticker is required parameter"},
            status=400,
        )

    res: dict = HermesAPI.get_earnings(ticker)
    resp = HermesEarningsSource(res).get()
    return JsonResponse(resp, status=200)


@require_GET  # type: ignore
def hermes_suggest(request: HttpRequest) -> JsonResponse:
    suggest_str: str = request.GET.get("s", None).lower()
    if not suggest_str:
        return JsonResponse(
            {"status": "false", "message": "s is required parameter"}, status=400
        )
    search: list = HermesAPI.search(suggest_str)
    return JsonResponse({"results": search}, status=200)


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
