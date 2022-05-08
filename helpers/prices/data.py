from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union, TypedDict
import datetime
import pandas as pd
import numpy as np
import numpy.typing as npt
from enum import Enum


class HermesPeriod(Enum):
    INTRADAY = 1
    DAILY = 2
    WEEKLY = 3
    MONTHLY = 4
    QUARTERLY = 5
    YEARLY = 6


class HermesHoldersResponse(TypedDict):
    inst_dates: List[str]
    inst_shares: List[float]
    inst_percent: List[float]
    inst_name: List[str]
    inst_change: List[float]
    inst_changep: List[float]
    fund_dates: List[str]
    fund_shares: List[float]
    fund_percent: List[float]
    fund_name: List[str]
    fund_change: List[float]
    fund_changep: List[float]


class HermesHoldersSource:
    def get(self) -> HermesHoldersResponse:
        institution = self.json_holders["Holders::Institutions"]
        funds = self.json_holders["Holders::Funds"]

        inst_dates = []
        inst_shares = []
        inst_percent = []
        inst_name = []
        inst_change = []
        inst_changep = []
        for row in institution:
            val = institution[row]
            inst_dates.append(val["date"])
            inst_shares.append(val["currentShares"])
            inst_percent.append(val["totalShares"])
            inst_name.append(val["name"])
            inst_change.append(val["change"])
            inst_changep.append(val["change_p"])

        fund_dates = []
        fund_shares = []
        fund_percent = []
        fund_name = []
        fund_change = []
        fund_changep = []
        for row in funds:
            val = institution[row]
            fund_dates.append(val["date"])
            fund_shares.append(val["currentShares"])
            fund_percent.append(val["totalShares"])
            fund_name.append(val["name"])
            fund_change.append(val["change"])
            fund_changep.append(val["change_p"])

        return HermesHoldersResponse(
            inst_dates=inst_dates,
            inst_shares=inst_shares,
            inst_percent=inst_percent,
            inst_name=inst_name,
            inst_change=inst_change,
            inst_changep=inst_changep,
            fund_dates=fund_dates,
            fund_shares=fund_shares,
            fund_percent=fund_percent,
            fund_name=fund_name,
            fund_change=fund_change,
            fund_changep=fund_changep,
        )

    def __init__(self, json_holders):
        self.json_holders = json_holders
        return


class HermesSummaryResponse(TypedDict):
    code: str
    name: str
    exchange: str
    currency: str
    sector: str
    gic_sector: str
    gic_group: str
    gic_industry: str
    gic_sub_industry: str
    market_cap: float
    pe_trail: float
    divi_yld: float
    eps_trail: float
    eps_curr_est: float
    eps_fwd_est: float
    eps_curr_q_est: float
    eps_next_q_est: float
    last_q_date: str
    fwd_pe: float
    tgt_price: float
    shares_outstanding: float
    shares_float: float
    shares_insider: float
    shares_inst: float


class HermesSummarySource:
    def get(self) -> HermesSummaryResponse:
        general = self.json_summary["General"]
        highlights = self.json_summary["Highlights"]
        shares = self.json_summary["SharesStats"]
        valuation = self.json_summary["Valuation"]
        return HermesSummaryResponse(
            code=general["Code"],
            name=general["Name"],
            exchange=general["Exchange"],
            currency=general["CurrencyCode"],
            sector=general["Sector"],
            gic_sector=general["GicSector"],
            gic_group=general["GicGroup"],
            gic_industry=general["GicIndustry"],
            gic_sub_industry=general["GicSubIndustry"],
            market_cap=float(highlights["MarketCapitalization"]) / 1000000,
            pe_trail=highlights["PERatio"],
            divi_yld=highlights["DividendYield"],
            eps_trail=highlights["EarningsShare"],
            eps_curr_est=highlights["EPSEstimateCurrentYear"],
            eps_fwd_est=highlights["EPSEstimateNextYear"],
            eps_curr_q_est=highlights["EPSEstimateCurrentQuarter"],
            eps_next_q_est=highlights["EPSEstimateNextQuarter"],
            last_q_date=highlights["MostRecentQuarter"],
            fwd_pe=valuation["ForwardPE"],
            tgt_price=highlights["WallStreetTargetPrice"],
            shares_outstanding=shares["SharesOutstanding"],
            shares_float=shares["SharesOutstanding"] / shares["SharesFloat"],
            shares_insider=shares["PercentInsiders"],
            shares_inst=shares["PercentInstitutions"],
        )

    def __init__(self, json_summary: Dict[Any, Any]):
        self.json_summary = json_summary
        return


class HermesEarningsResponse(TypedDict):
    eps_actual: List[float]
    eps_est: List[float]
    eps_diff: List[float]
    eps_dates_period: List[str]
    eps_dates_report: List[str]
    eps_est_period: List[str]
    eps_est_avg: List[float]
    eps_est_year_ago: List[float]
    eps_est_trend_thirty: List[float]
    eps_est_trend_ninety: List[float]
    rev_est_avg: List[float]
    eps_est_analyst_no: List[float]
    eps_est_dates: List[str]


class HermesEarningsSource:
    def get(self) -> Any:
        history = self.json_earnings["Earnings::History"]
        trend = self.json_earnings["Earnings::Trend"]
        eps_actual = []
        eps_est = []
        eps_diff = []
        eps_dates_period = []
        eps_dates_report = []
        for date in history:
            row = history[date]
            eps_actual.append(row["epsActual"])
            eps_est.append(row["epsEstimate"])
            eps_diff.append(row["epsDifference"])
            eps_dates_period.append(row["date"])
            eps_dates_report.append(row["reportDate"])

        eps_est_period = []
        eps_est_avg = []
        eps_est_year_ago = []
        eps_est_trend_thirty = []
        eps_est_trend_ninety = []
        rev_est_avg = []
        eps_est_analyst_no = []
        eps_est_dates = []
        for date in trend:
            row = trend[date]
            eps_est_period.append(row["period"])
            eps_est_avg.append(row["earningsEstimateAvg"])
            eps_est_year_ago.append(row["earningsEstimateYearAgoEps"])
            eps_est_trend_thirty.append(row["epsTrend30daysAgo"])
            eps_est_trend_ninety.append(row["epsTrend90daysAgo"])
            rev_est_avg.append(row["revenueEstimateAvg"])
            eps_est_analyst_no.append(row["earningsEstimateNumberOfAnalysts"])
            eps_est_dates.append(date)

        return HermesEarningsResponse(
            eps_actual=eps_actual,
            eps_est=eps_est,
            eps_diff=eps_diff,
            eps_dates_period=eps_dates_period,
            eps_dates_report=eps_dates_report,
            eps_est_period=eps_est_period,
            eps_est_avg=eps_est_avg,
            eps_est_year_ago=eps_est_year_ago,
            eps_est_trend_thirty=eps_est_trend_thirty,
            eps_est_trend_ninety=eps_est_trend_ninety,
            rev_est_avg=rev_est_avg,
            eps_est_analyst_no=eps_est_analyst_no,
            eps_est_dates=eps_est_dates,
        )

    def __init__(self, json_earnings: Dict[Any, Any]):
        self.json_earnings = json_earnings
        return


class HermesFundamentalResponse(TypedDict):
    revenue: List[float]
    ebit: List[float]
    op_inc: List[float]
    net_inc: List[float]
    cash: List[float]
    net_wc: List[float]
    net_tang: List[float]
    tot_assets: List[float]
    st_debt: List[float]
    lt_debt: List[float]
    tot_debt: List[float]
    leases: List[float]
    net_debt: List[float]
    tot_equity: List[float]
    chg_wc: List[float]
    cfo: List[float]
    capex: List[float]
    cff: List[float]
    chg_cash: List[float]
    dates: List[str]
    titles: Dict[str, Dict[str, str]]


FundiesStruct = Dict[str, Dict[str, Union[float, str]]]

always_zero = lambda x: 0 if not x else float(x)
sometimes_none = lambda x: -1 if not x else float(x)


class HermesFundamentalSource:
    date_fmt: str = "%Y-%m-%d"
    num_fmt: int = 1000000  ##1m

    titles: Dict[str, Dict[str, str]] = {
        "Income Stmt": {
            "revenue": "Revenue",
            "ebit": "EBIT",
            "op_inc": "Op Inc",
            "net_inc": "Net Inc",
        },
        "Balance Sht": {
            "cash": "Cash",
            "net_wc": "Net WC",
            "net_tang": "Net Tang",
            "tot_assets": "Tot Assets",
            "st_debt": "ST Debt",
            "lt_debt": "LT Debt",
            "tot_debt": "Tot Debt",
            "leases": "Leases",
            "net_debt": "Net Debt",
            "tot_equity": "Tot Eq",
        },
        "Cash Flow Stmt": {
            "chg_wc": "Chg WC",
            "cfo": "CFO",
            "capex": "Capex",
            "cff": "CFF",
            "chg_cash": "Chg Cash",
        },
    }

    inc_names: List[Callable[[Dict[str, float]], float]] = [
        lambda x: sometimes_none(x["totalRevenue"]),
        lambda x: sometimes_none(x["ebit"]),
        lambda x: sometimes_none(x["operatingIncome"]),
        lambda x: sometimes_none(x["netIncome"]),
    ]

    bal_names: List[Callable[[Dict[str, float]], float]] = [
        lambda x: always_zero(x["cash"]) + always_zero(x["shortTermInvestments"]),
        lambda x: always_zero(x["totalCurrentAssets"])
        - always_zero(x["totalCurrentLiabilities"]),
        lambda x: always_zero(x["totalAssets"])
        - always_zero(x["intangibleAssets"])
        + always_zero(x["goodWill"])
        - always_zero(x["totalLiab"]),
        lambda x: sometimes_none(x["totalAssets"]),
        lambda x: sometimes_none(x["shortTermDebt"]),
        lambda x: sometimes_none(x["longTermDebt"]),
        lambda x: sometimes_none(x["shortLongTermDebtTotal"]),
        lambda x: sometimes_none(x["capitalLeaseObligations"]),
        lambda x: always_zero(x["shortLongTermDebtTotal"])
        - always_zero(x["cash"])
        - always_zero(x["shortTermInvestments"]),
        lambda x: always_zero(x["totalAssets"]) - always_zero(x["totalLiab"]),
    ]

    cash_names: List[Callable[[Dict[str, float]], float]] = [
        lambda x: sometimes_none(x["changeInWorkingCapital"]),
        lambda x: sometimes_none(x["totalCashFromOperatingActivities"]),
        lambda x: sometimes_none(x["capitalExpenditures"]),
        lambda x: sometimes_none(x["totalCashFromFinancingActivities"]),
        lambda x: sometimes_none(x["changeInCash"]),
    ]

    def _parse_dates(self, statement: FundiesStruct) -> List[float]:
        ##We can have multiple dates for one year of results, likely due to restatments
        ##and differences between prelim/annual reporting. For dates, we just want to
        ##display the first date to the user because that is the period end for the
        ##results
        res: List[float] = []
        last_year = -1
        for date in statement:
            curr_year = date[0:4]
            if last_year == curr_year:
                res[-1] = date
            else:
                res.append(date)
                last_year = curr_year
        return res

    def _parse_statement(
        self, statement: FundiesStruct, variable_names: List[str]
    ) -> List[List[float]]:
        res: List[List[float]] = []
        last_year = -1
        ##Problem here is that single years can have multiple rows of data,
        ##some of which may be none. This is likely due to restatements and
        ##differences between prelim/annual reporting.
        ##To get the right data we track the current year and add if we
        ##are missing that data.
        ##Note that algo for getting date is different because we use the period
        ##date which is the earliest date for a single year. So the data actually isn't
        ##strictly matched to the date shown to the user.
        for date in statement:
            curr_year: str = date[0:4]
            if curr_year == last_year:
                ##We have existing values, only replace missing
                existing_vals = res[-1]
                for pos, val in enumerate(existing_vals):
                    if not val:
                        missing_name: Callable[
                            [Dict[str, float]], float
                        ] = variable_names[pos]
                        val: Union[float, None] = missing_name(statement[date])
                        ## Edit res in place
                        if val:
                            existing_vals[pos] = (
                                float(val) / HermesFundamentalSource.num_fmt
                            )
                        else:
                            existing_vals[pos] = val
            else:
                temp: List[float] = []
                for name_func in variable_names:
                    val: Union[float, None] = name_func(statement[date])
                    if val:
                        temp.append(float(val) / HermesFundamentalSource.num_fmt)
                    else:
                        temp.append(val)
                res.append(temp)
                last_year = curr_year
        return list(zip(*res))

    def get(self) -> HermesFundamentalResponse:
        query = lambda x: f"Financials::{x}::yearly"
        inc_statement: FundiesStruct = self.json_fundamental[query("Income_Statement")]
        bal_statement: FundiesStruct = self.json_fundamental[query("Balance_Sheet")]
        cash_statement: FundiesStruct = self.json_fundamental[query("Cash_Flow")]

        dates: List[float] = self._parse_dates(inc_statement)
        parsed_inc = self._parse_statement(
            inc_statement, HermesFundamentalSource.inc_names
        )
        parsed_bal = self._parse_statement(
            bal_statement, HermesFundamentalSource.bal_names
        )
        parsed_cash = self._parse_statement(
            cash_statement, HermesFundamentalSource.cash_names
        )
        return HermesFundamentalResponse(
            revenue=parsed_inc[0],
            ebit=parsed_inc[1],
            op_inc=parsed_inc[2],
            net_inc=parsed_inc[3],
            cash=parsed_bal[0],
            net_wc=parsed_bal[1],
            net_tang=parsed_bal[2],
            tot_assets=parsed_bal[3],
            st_debt=parsed_bal[4],
            lt_debt=parsed_bal[5],
            tot_debt=parsed_bal[6],
            leases=parsed_bal[7],
            net_debt=parsed_bal[8],
            tot_equity=parsed_bal[9],
            chg_wc=parsed_cash[0],
            cfo=parsed_cash[1],
            capex=parsed_cash[2],
            cff=parsed_cash[3],
            chg_cash=parsed_cash[4],
            dates=dates,
            titles=HermesFundamentalSource.titles,
        )

    def __init__(self, json_fundamental: Dict[Any, Any], period: HermesPeriod):
        self.json_fundamental = json_fundamental
        self.period = period
        return


class HermesDailyResponse(TypedDict):
    dates: List[int]
    close: List[float]


class HermesPriceSource:

    daily_date_fmt = "%Y-%m-%d"
    intraday_date_fmt = ""

    def get(self) -> HermesDailyResponse:
        dates = []
        closes = []
        for row in self.json_price:
            ts = datetime.datetime.strptime(
                row["date"], HermesPriceSource.daily_date_fmt
            ).timestamp()
            dates.append(int(ts))
            closes.append(float(row["adjusted_close"]))
        return HermesDailyResponse(dates=dates, close=closes)

    def __init__(self, json_price: List, period: HermesPeriod):
        self.json_price = json_price
        self.period = period
        return


class FactorSource:
    def convert_to_monthly(self) -> None:
        ##Moves error into runtime, not ideal but anything else
        ##will require re-working more code
        raise NotImplementedError

    def get_length(self) -> int:
        return len(self.data)

    def get_dates(self) -> pd.Index:
        return self.data.index

    def get_prices(self) -> pd.DataFrame:
        return self.data

    def get_factors(self) -> npt.NDArray[np.str0]:
        return self.data["factor"].unique()  # type: ignore

    def get_returns(self) -> pd.DataFrame:
        return self.data[["ret"]]

    def get_returns_list(self) -> npt.NDArray[np.float64]:
        return self.get_returns()["ret"].to_numpy(dtype=np.float64)  # type:ignore

    def __init__(self, df: pd.DataFrame):
        self.data: pd.DataFrame = pd.DataFrame({})
        if "period" not in df.columns:
            self.data = df
        else:
            df["period"] = pd.to_numeric(df["period"])
            df.set_index("period", inplace=True)
            self.data = df
        return


class InvestPySource:
    def convert_to_monthly(self) -> None:
        ##Non-idempotent
        self.data.index = pd.to_datetime(self.data.index, unit="s")
        df: pd.DataFrame = self.data.groupby(
            by=[self.data.index.year, self.data.index.month]
        ).last()
        df.index.set_names(["year", "month"], inplace=True)
        df.reset_index(inplace=True)
        df["ret"] = round(df["Close"].pct_change(1) * 100, 3)
        df["time"] = pd.to_datetime(
            df["year"].astype(str) + "-" + df["month"].astype(str), format="%Y-%m"
        )
        df["time"] = df["time"].apply(lambda x: int(x.timestamp() * 1))
        filtered: pd.DataFrame = df[["time", "ret", "Open", "Close"]].copy()
        filtered.set_index("time", inplace=True)
        filtered.dropna(inplace=True)
        self.data: pd.DataFrame = filtered
        return

    def get_length(self) -> int:
        return len(self.data)

    def get_dates(self) -> pd.Index:
        return self.data.index

    def get_prices(self) -> pd.DataFrame:
        return self.data[["Open", "Close"]]

    def get_returns(self) -> pd.DataFrame:
        return self.data[["ret"]]

    def get_returns_list(self) -> npt.NDArray[np.float64]:
        return self.get_returns()["ret"].to_numpy(dtype=np.float64)  # type: ignore

    def __init__(self, df: pd.DataFrame):
        if "ret" in df.columns:
            self.data: pd.DataFrame = df
            return
        else:
            df.reset_index(inplace=True)
            df["ret"] = round(df["Close"].pct_change(1) * 100, 3)
            df.dropna(inplace=True)
            df["time"] = df["Date"].apply(lambda x: int(x.timestamp() * 1))
            filtered: pd.DataFrame = df[["time", "ret", "Open", "Close"]]
            filtered.set_index("time", inplace=True)
            self.data: pd.DataFrame = filtered  # type: ignore
            self.length: int = len(filtered)


DataSource = Union[FactorSource, InvestPySource]

T = TypeVar("T", bound=DataSource)


class SourceFactory:
    @staticmethod
    def find_dates(dates: List[pd.Timestamp], data: T, cls: Type[T]) -> DataSource:
        return cls(data.data.loc[dates])

    @staticmethod
    def find_index(
        start: pd.Timestamp, end: pd.Timestamp, data: T, cls: Type[T]
    ) -> DataSource:
        return cls(data.data.iloc[start:end])


class FakeData:
    @staticmethod
    def get_investpy(
        mean: float, stdev: float, length: int = 100, seed: Optional[int] = None
    ) -> InvestPySource:
        if seed:
            np.random.seed(seed)

        dates: List[pd.Timestamp] = [
            pd.Timestamp(datetime.date(2000, 9, 1)) + pd.DateOffset(days=i)
            for i in range(length)
        ]

        idx = pd.Index(data=dates, name="Date")
        df = pd.DataFrame(
            {
                "Close": np.random.normal(mean, stdev, length),
                "Open": np.random.normal(mean, stdev, length),
            },
            index=idx,
        )
        return InvestPySource(df)

    @staticmethod
    def get_factor(
        mean: float, stdev: float, length: int = 100, seed: Optional[int] = None
    ) -> FactorSource:
        if seed:
            np.random.seed(seed)

        factor_dates: List[int] = [
            (
                pd.Timestamp(datetime.date(2001, 9, 1)) + pd.DateOffset(months=i)
            ).timestamp()
            for i in range(length)
        ]

        df = pd.DataFrame(
            {
                "factor": "Mkt",
                "ret": np.random.normal(mean, stdev, length) * 100,
                "name": "fake_factor",
                "period": factor_dates,
                "period_name": list([(str(i) + "fake_factor") for i in range(length)]),
            }
        )
        return FactorSource(df)
