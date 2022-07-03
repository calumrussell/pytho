# type: ignore
from functools import wraps
from typing import Any, Callable, List, TypedDict, Union
from django.http.request import HttpRequest
from django.http.response import JsonResponse

from api.models import Coverage
from helpers.analysis.riskattribution import RegressionInput, RollingRegressionInput


def regression_input(has_window: bool = False):
    """
    Formats query string variables used in routes that
    need regression-type inputs. Will throw errors from
    here if these inputs are invalid.
    """

    def decorator(func):
        @wraps(func)
        def inner(
            request: HttpRequest, *args, **kwargs
        ) -> Union[JsonResponse, Callable[[Any], Any]]:

            if not request.method == "GET":
                return JsonResponse({}, status=405)

            ind: List[str] = request.GET.getlist("ind", None)
            dep: str = request.GET.get("dep", None)

            if not ind or not dep:
                return JsonResponse(
                    {
                        "status": "false",
                        "message": "Must pass at least one independent and only one dependent to risk attribution",
                    },
                    status=400,
                )

            dep_digit: int
            if dep.isdigit():
                dep_digit = int(dep)
            else:
                return JsonResponse(
                    {"status": "false", "message": "Dependent isn't a number"},
                    status=400,
                )

            ind_digit: List[int]
            is_ind_ints: bool = len(list(filter(lambda x: x.isdigit(), ind))) == len(
                ind
            )
            if is_ind_ints:
                ind_digit = list(map(lambda x: int(x), ind))
            else:
                return JsonResponse(
                    {
                        "status": "false",
                        "message": "Independent has at least one non-number input",
                    },
                    status=400,
                )

            coverage_ids: List[int] = [dep_digit, *ind_digit]
            try:
                coverage: List[Coverage] = Coverage.objects.filter(id__in=coverage_ids)
            except Exception:
                return JsonResponse(
                    {"status": "false", "message": "Invalid asset ids"}, status=400
                )
            else:
                """If we do not have coverage for at least one asset id passed by client
                then we need to exit the analysis with error. This will also fail with
                non-unique asset ids
                """
                if not coverage or len(coverage) != len(coverage_ids):
                    return JsonResponse(
                        {"status": "false", "message": "Invalid or missing asset ids"},
                        status=404,
                    )

            if has_window:
                window_digit: int
                window: str = request.GET.get("window", "6")
                if window.isdigit():
                    window_digit = int(window)
                else:
                    return JsonResponse(
                        {"status": "false", "message": "Window must be a number"},
                        status=400,
                    )

                rolling: RollingRegressionInput = RollingRegressionInput(
                    ind=ind_digit, dep=dep_digit, window=window_digit
                )
                return func(
                    request, regression=rolling, coverage=coverage, *args, **kwargs
                )

            regression = RegressionInput(ind=ind_digit, dep=dep_digit)
            return func(
                request, regression=regression, coverage=coverage, *args, **kwargs
            )

        return inner

    return decorator
