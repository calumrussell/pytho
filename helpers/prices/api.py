from datetime import date
from typing import Dict, List

from django.db.models.query import QuerySet
import investpy
import pandas as pd

from api.models import Coverage, FactorReturns

from .data import DataSource, FactorSource, InvestPySource


class PriceAPIRequestMonthly:
    def get(self) -> DataSource:
        ##Don't require transform for factor because they are
        ##already monthly
        res: DataSource = self.price_api.get()
        if self.coverage.security_type == "factor":
            return res
        else:
            res.convert_to_monthly()
            return res

    def __init__(self, coverage_obj: Coverage) -> None:
        self.coverage = coverage_obj
        self.price_api = PriceAPIRequest(coverage_obj)
        pass


class PriceAPIRequest:
    def get(self) -> DataSource:
        if self.coverage.security_type == "etf":
            return InvestPySource(
                PriceAPI.get_etf_price_history(
                    self.coverage.name, self.coverage.country_name
                )
            )

        elif self.coverage.security_type == "index":
            return InvestPySource(
                PriceAPI.get_index_price_history(
                    self.coverage.name, self.coverage.country_name
                )
            )

        elif self.coverage.security_type == "fund":
            return InvestPySource(
                PriceAPI.get_fund_price_history(
                    self.coverage.name, self.coverage.country_name
                )
            )

        elif self.coverage.security_type == "stock":
            return InvestPySource(
                PriceAPI.get_stock_price_history(
                    self.coverage.ticker, self.coverage.country_name
                )
            )

        elif self.coverage.security_type == "factor":
            return FactorSource(FactorAPI.get_factor_price_history(self.coverage.name))
        else:
            raise ValueError("Unknown security type")

    def __init__(self, coverage_obj: Coverage):
        self.coverage: Coverage = coverage_obj


class PriceAPIRequestsMonthly:
    def get(self) -> Dict[int, DataSource]:
        return {int(i.id): j.get() for i, j in zip(self.coverage, self.requests)}  # type: ignore

    def __init__(self, coverage_objs: List[Coverage]):
        self.coverage: List[Coverage] = coverage_objs
        self.requests: List[PriceAPIRequestMonthly] = [
            PriceAPIRequestMonthly(i) for i in coverage_objs
        ]


class PriceAPIRequests:
    def get(self) -> Dict[int, DataSource]:
        return {int(i.id): j.get() for i, j in zip(self.coverage, self.requests)}  # type: ignore

    def get_overlapping(self) -> Dict[int, DataSource]:
        sources = [request.get() for request in self.requests]
        dates = [set(source.get_dates()) for source in sources]
        date_intersection = sorted(set.intersection(*dates))
        filtered_sources = [
            source.filter_dates(date_intersection) for source in sources
        ]
        return {int(i.id): source for i, source in zip(self.coverage, filtered_sources)}  # type: ignore

    def __init__(self, coverage_objs: QuerySet[Coverage]):
        self.coverage = coverage_objs
        self.requests = [PriceAPIRequest(i) for i in coverage_objs]


class FactorAPI:
    @staticmethod
    def get_factor_price_history(name: str) -> pd.DataFrame:
        # Need to split off the factor
        split = name.split("-")
        join_factor = "-".join(split[1:])
        res = FactorReturns.objects.filter(name=split[0], factor=join_factor)
        temp = [i.__dict__ for i in res]
        return pd.DataFrame(temp)


class PriceAPI:

    current_date: str = date.today().strftime("%d/%m/%Y")

    @staticmethod
    def get_etf_price_history(etf: str, country: str) -> pd.DataFrame:
        return investpy.get_etf_historical_data(
            etf=etf,
            country=country,
            from_date="01/01/1970",
            to_date=PriceAPI.current_date,
        )

    @staticmethod
    def get_index_price_history(index: str, country: str) -> pd.DataFrame:
        return investpy.get_index_historical_data(
            index=index,
            country=country,
            from_date="01/01/1970",
            to_date=PriceAPI.current_date,
        )

    @staticmethod
    def get_fund_price_history(fund: str, country: str) -> pd.DataFrame:
        return investpy.get_fund_historical_data(
            fund=fund,
            country=country,
            from_date="01/01/1970",
            to_date=PriceAPI.current_date,
        )

    @staticmethod
    def get_stock_price_history(security: str, country: str) -> pd.DataFrame:
        return investpy.get_stock_historical_data(
            stock=security,
            country=country,
            from_date="01/01/1970",
            to_date=PriceAPI.current_date,
        )
