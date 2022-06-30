from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union, TypedDict
import datetime
import pandas as pd
import numpy as np
import numpy.typing as npt
from enum import Enum


class FactorSource:
    def convert_to_monthly(self) -> None:
        ##Moves error into runtime, not ideal but anything else
        ##will require re-working more code
        raise NotImplementedError

    def get_length(self) -> int:
        return len(self.data)

    def get_dates(self) -> pd.Index:
        return self.data.index

    def get_close(self) -> pd.DataFrame:
        return self.data

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

    def get_close(self) -> pd.DataFrame:
        return self.data[["Close"]]

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
