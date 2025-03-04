from collections.abc import (
    Hashable,
    Iterator,
)
from typing import Union

import numpy as np
import pandas as pd
from pandas import (
    DataFrame,
    DatetimeIndex,
    Index,
    Series,
    date_range,
)
from pandas.core.groupby.generic import (
    DataFrameGroupBy,
    SeriesGroupBy,
)
from pandas.core.resample import DatetimeIndexResampler
from typing_extensions import assert_type

from tests import (
    PD_LTE_21,
    TYPE_CHECKING_INVALID_USAGE,
    check,
    pytest_warns_bounded,
)

DR = date_range("1999-1-1", periods=365, freq="D")
DF_ = DataFrame(np.random.standard_normal((365, 1)), index=DR)
S = DF_.iloc[:, 0]
DF = DataFrame({"col1": S, "col2": S})


_AggRetType = Union[DataFrame, Series]

if PD_LTE_21:
    MonthFreq = "M"
else:
    MonthFreq = "ME"


def test_props() -> None:
    check(assert_type(DF.resample(MonthFreq).obj, DataFrame), DataFrame)
    check(assert_type(DF.resample(MonthFreq).ax, Index), DatetimeIndex)


def test_iter() -> None:
    assert_type(iter(DF.resample(MonthFreq)), Iterator[tuple[Hashable, DataFrame]])
    for v in DF.resample(MonthFreq):
        check(assert_type(v, tuple[Hashable, DataFrame]), tuple)


def test_agg_funcs() -> None:
    check(assert_type(DF.resample(MonthFreq).sum(), DataFrame), DataFrame)
    check(assert_type(DF.resample(MonthFreq).prod(), DataFrame), DataFrame)
    check(assert_type(DF.resample(MonthFreq).min(), DataFrame), DataFrame)
    check(assert_type(DF.resample(MonthFreq).max(), DataFrame), DataFrame)
    check(assert_type(DF.resample(MonthFreq).first(), DataFrame), DataFrame)
    check(assert_type(DF.resample(MonthFreq).last(), DataFrame), DataFrame)
    check(assert_type(DF.resample(MonthFreq).mean(), DataFrame), DataFrame)
    check(assert_type(DF.resample(MonthFreq).sum(), DataFrame), DataFrame)
    check(assert_type(DF.resample(MonthFreq).median(), DataFrame), DataFrame)
    check(assert_type(DF.resample(MonthFreq).ohlc(), DataFrame), DataFrame)
    check(assert_type(DF.resample(MonthFreq).nunique(), DataFrame), DataFrame)


def test_quantile() -> None:
    check(assert_type(DF.resample(MonthFreq).quantile(0.5), DataFrame), DataFrame)
    check(
        assert_type(DF.resample(MonthFreq).quantile([0.5, 0.7]), DataFrame), DataFrame
    )
    check(
        assert_type(DF.resample(MonthFreq).quantile(np.array([0.5, 0.7])), DataFrame),
        DataFrame,
    )


def test_std_var() -> None:
    check(assert_type(DF.resample(MonthFreq).std(), DataFrame), DataFrame)
    check(assert_type(DF.resample(MonthFreq).var(2), DataFrame), DataFrame)


def test_size_count() -> None:
    check(assert_type(DF.resample(MonthFreq).size(), "Series[int]"), Series, np.integer)
    check(assert_type(DF.resample(MonthFreq).count(), DataFrame), DataFrame)


def test_filling() -> None:
    check(assert_type(DF.resample(MonthFreq).ffill(), DataFrame), DataFrame)
    check(assert_type(DF.resample(MonthFreq).nearest(), DataFrame), DataFrame)
    check(assert_type(DF.resample(MonthFreq).bfill(), DataFrame), DataFrame)


def test_fillna() -> None:
    # deprecated (and removed from stub)
    if TYPE_CHECKING_INVALID_USAGE:
        DF.resample(MonthFreq).fillna("pad")  # type: ignore[operator]  # pyright: ignore


def test_aggregate() -> None:
    with pytest_warns_bounded(
        FutureWarning,
        r"The provided callable <function (sum|mean) .*> is currently using ",
        lower="2.0.99",
    ):
        check(
            assert_type(DF.resample(MonthFreq).aggregate(np.sum), DataFrame), DataFrame
        )
        check(assert_type(DF.resample(MonthFreq).agg(np.sum), DataFrame), DataFrame)
        check(assert_type(DF.resample(MonthFreq).apply(np.sum), DataFrame), DataFrame)
        check(
            assert_type(DF.resample(MonthFreq).aggregate([np.sum, np.mean]), DataFrame),
            DataFrame,
        )
        check(
            assert_type(DF.resample(MonthFreq).aggregate(["sum", np.mean]), DataFrame),
            DataFrame,
        )
        check(
            assert_type(
                DF.resample(MonthFreq).aggregate({"col1": "sum", "col2": np.mean}),
                DataFrame,
            ),
            DataFrame,
        )
        check(
            assert_type(
                DF.resample(MonthFreq).aggregate(
                    {"col1": ["sum", np.mean], "col2": np.mean}
                ),
                DataFrame,
            ),
            DataFrame,
        )

    def f(val: DataFrame) -> Series:
        return val.mean()

    check(assert_type(DF.resample(MonthFreq).aggregate(f), DataFrame), DataFrame)


def test_asfreq() -> None:
    check(assert_type(DF.resample(MonthFreq).asfreq(-1.0), DataFrame), DataFrame)


def test_getattr() -> None:
    check(assert_type(DF.resample(MonthFreq).col1, SeriesGroupBy), SeriesGroupBy)


def test_interpolate() -> None:
    check(assert_type(DF.resample(MonthFreq).interpolate(), DataFrame), DataFrame)
    check(
        assert_type(DF.resample(MonthFreq).interpolate(method="time"), DataFrame),
        DataFrame,
    )


def test_interpolate_inplace() -> None:
    check(
        assert_type(DF.resample(MonthFreq).interpolate(inplace=True), None), type(None)
    )


def test_pipe() -> None:
    def f(val: "DatetimeIndexResampler[DataFrame]") -> DataFrame:
        assert isinstance(val, DatetimeIndexResampler)
        return DataFrame(val)

    check(assert_type(DF.resample(MonthFreq).pipe(f), DataFrame), DataFrame)

    def g(val: "DatetimeIndexResampler[DataFrame]") -> DataFrame:
        assert isinstance(val, DatetimeIndexResampler)
        return val.mean()

    check(assert_type(DF.resample(MonthFreq).pipe(g), DataFrame), DataFrame)

    def h(val: "DatetimeIndexResampler[DataFrame]") -> Series:
        assert isinstance(val, DatetimeIndexResampler)
        return val.mean().mean()

    check(assert_type(DF.resample(MonthFreq).pipe(h), Series), Series)

    def i(val: "DatetimeIndexResampler[DataFrame]") -> float:
        assert isinstance(val, DatetimeIndexResampler)
        return float(val.mean().mean().mean())

    check(assert_type(DF.resample(MonthFreq).pipe(i), float), float)

    def j(
        res: "DatetimeIndexResampler[DataFrame]",
        pos: int,
        /,
        arg1: list[float],
        arg2: str,
        *,
        kw: tuple[int],
    ) -> DataFrame:
        assert isinstance(res, DatetimeIndexResampler)
        return res.obj

    check(
        assert_type(
            DF.resample(MonthFreq).pipe(j, 1, [1.0], arg2="hi", kw=(1,)), DataFrame
        ),
        DataFrame,
    )

    if TYPE_CHECKING_INVALID_USAGE:
        DF.resample(MonthFreq).pipe(
            j,
            "a",  # type: ignore[arg-type] # pyright: ignore[reportGeneralTypeIssues]
            [1.0, 2.0],
            arg2="hi",
            kw=(1,),
        )
        DF.resample(MonthFreq).pipe(
            j,
            1,
            [1.0, "b"],  # type: ignore[list-item] # pyright: ignore[reportGeneralTypeIssues]
            arg2="hi",
            kw=(1,),
        )
        DF.resample(MonthFreq).pipe(
            j,
            1,
            [1.0],
            arg2=11,  # type: ignore[arg-type] # pyright: ignore[reportGeneralTypeIssues]
            kw=(1,),
        )
        DF.resample(MonthFreq).pipe(
            j,
            1,
            [1.0],
            arg2="hi",
            kw=(1, 2),  # type: ignore[arg-type] # pyright: ignore[reportGeneralTypeIssues]
        )
        DF.resample(MonthFreq).pipe(  # type: ignore[call-arg]
            j,
            1,
            [1.0],
            arg3="hi",  # pyright: ignore[reportGeneralTypeIssues]
            kw=(1,),
        )
        DF.resample(MonthFreq).pipe(  # type: ignore[misc]
            j,
            1,
            [1.0],
            11,  # type: ignore[arg-type]
            (1,),  # pyright: ignore[reportGeneralTypeIssues]
        )
        DF.resample(MonthFreq).pipe(  # type: ignore[call-arg]
            j,
            pos=1,  # pyright: ignore[reportGeneralTypeIssues]
            arg1=[1.0],
            arg2=11,  # type: ignore[arg-type]
            kw=(1,),
        )

    def k(x: int, t: "DatetimeIndexResampler[DataFrame]") -> DataFrame:
        assert isinstance(x, int)
        return t.obj

    check(assert_type(DF.resample(MonthFreq).pipe((k, "t"), 1), DataFrame), DataFrame)

    if TYPE_CHECKING_INVALID_USAGE:
        DF.resample(MonthFreq).pipe(
            (k, 1),  # type: ignore[arg-type] # pyright: ignore[reportGeneralTypeIssues]
            1,
        )


def test_transform() -> None:
    def f(val: Series) -> Series:
        return -1 * val

    check(assert_type(DF.resample(MonthFreq).transform(f), DataFrame), DataFrame)


def test_props_series() -> None:
    check(assert_type(S.resample(MonthFreq).obj, Series), Series)
    check(assert_type(S.resample(MonthFreq).ax, Index), DatetimeIndex)


def test_iter_series() -> None:
    for v in S.resample(MonthFreq):
        check(assert_type(v, tuple[Hashable, Series]), tuple)


def test_agg_funcs_series() -> None:
    check(assert_type(S.resample(MonthFreq).sum(), Series), Series)
    check(assert_type(S.resample(MonthFreq).prod(), Series), Series)
    check(assert_type(S.resample(MonthFreq).min(), Series), Series)
    check(assert_type(S.resample(MonthFreq).max(), Series), Series)
    check(assert_type(S.resample(MonthFreq).first(), Series), Series)
    check(assert_type(S.resample(MonthFreq).last(), Series), Series)
    check(assert_type(S.resample(MonthFreq).mean(), Series), Series)
    check(assert_type(S.resample(MonthFreq).sum(), Series), Series)
    check(assert_type(S.resample(MonthFreq).median(), Series), Series)
    check(assert_type(S.resample(MonthFreq).ohlc(), DataFrame), DataFrame)
    check(
        assert_type(S.resample(MonthFreq).nunique(), "Series[int]"), Series, np.integer
    )


def test_quantile_series() -> None:
    check(assert_type(S.resample(MonthFreq).quantile(0.5), Series), Series)
    check(assert_type(S.resample(MonthFreq).quantile([0.5, 0.7]), Series), Series)
    check(
        assert_type(S.resample(MonthFreq).quantile(np.array([0.5, 0.7])), Series),
        Series,
    )


def test_std_var_series() -> None:
    check(assert_type(S.resample(MonthFreq).std(), Series), Series)
    check(assert_type(S.resample(MonthFreq).var(2), Series), Series)


def test_size_count_series() -> None:
    check(assert_type(S.resample(MonthFreq).size(), "Series[int]"), Series, np.integer)
    check(assert_type(S.resample(MonthFreq).count(), "Series[int]"), Series, np.integer)


def test_filling_series() -> None:
    check(assert_type(S.resample(MonthFreq).ffill(), Series), Series)
    check(assert_type(S.resample(MonthFreq).nearest(), Series), Series)
    check(assert_type(S.resample(MonthFreq).bfill(), Series), Series)


def test_fillna_series() -> None:
    # deprecated (and removed from stub)
    if TYPE_CHECKING_INVALID_USAGE:
        S.resample(MonthFreq).fillna("pad")  # type: ignore[operator]  # pyright: ignore


def test_aggregate_series() -> None:
    with pytest_warns_bounded(
        FutureWarning,
        r"The provided callable <function (sum|mean) .*> is currently using ",
        lower="2.0.99",
    ):
        check(assert_type(S.resample(MonthFreq).aggregate(np.sum), _AggRetType), Series)
        check(assert_type(S.resample(MonthFreq).agg(np.sum), _AggRetType), Series)
        check(assert_type(S.resample(MonthFreq).apply(np.sum), _AggRetType), Series)
        check(
            assert_type(
                S.resample(MonthFreq).aggregate([np.sum, np.mean]), _AggRetType
            ),
            DataFrame,
        )
        check(
            assert_type(S.resample(MonthFreq).aggregate(["sum", np.mean]), _AggRetType),
            DataFrame,
        )
        check(
            assert_type(
                S.resample(MonthFreq).aggregate({"col1": "sum", "col2": np.mean}),
                _AggRetType,
            ),
            DataFrame,
        )

    def f(val: Series) -> float:
        return val.mean()

    check(assert_type(S.resample(MonthFreq).aggregate(f), _AggRetType), Series)


def test_asfreq_series() -> None:
    check(assert_type(S.resample(MonthFreq).asfreq(-1.0), Series), Series)


def test_interpolate_series() -> None:
    check(assert_type(S.resample(MonthFreq).interpolate(), Series), Series)
    check(assert_type(S.resample(MonthFreq).interpolate(method="time"), Series), Series)


def test_interpolate_inplace_series() -> None:
    check(
        assert_type(S.resample(MonthFreq).interpolate(inplace=True), None), type(None)
    )


def test_pipe_series() -> None:
    def f(val: "DatetimeIndexResampler[Series]") -> Series:
        assert isinstance(val, DatetimeIndexResampler)
        return Series(val)

    check(assert_type(S.resample(MonthFreq).pipe(f), Series), Series)

    def g(val: "DatetimeIndexResampler[Series]") -> float:
        assert isinstance(val, DatetimeIndexResampler)
        return float(val.mean().mean())

    check(assert_type(S.resample(MonthFreq).pipe(g), float), float)

    def h(val: "DatetimeIndexResampler[Series]") -> DataFrame:
        assert isinstance(val, DatetimeIndexResampler)
        return DataFrame({0: val, 1: val})

    check(assert_type(S.resample(MonthFreq).pipe(h), DataFrame), DataFrame)


def test_transform_series() -> None:
    def f(val: Series) -> Series:
        return -1 * val

    check(assert_type(S.resample(MonthFreq).transform(f), Series), Series)


def test_aggregate_series_combinations() -> None:
    def s2series(val: Series) -> Series:
        return pd.Series(val)

    def s2scalar(val: Series) -> float:
        return float(val.mean())

    with pytest_warns_bounded(
        FutureWarning,
        r"The provided callable <function (sum|mean) .*> is currently using ",
        lower="2.0.99",
    ):
        check(S.resample(MonthFreq).aggregate(np.sum), Series)
        check(S.resample(MonthFreq).aggregate([np.mean]), DataFrame)
        check(S.resample(MonthFreq).aggregate(["sum", np.mean]), DataFrame)
        check(S.resample(MonthFreq).aggregate({"sum": np.sum}), DataFrame)
        check(
            S.resample(MonthFreq).aggregate({"sum": np.sum, "mean": np.mean}), DataFrame
        )
    check(S.resample(MonthFreq).aggregate("sum"), Series)
    check(S.resample(MonthFreq).aggregate(s2series), Series)
    check(S.resample(MonthFreq).aggregate(s2scalar), Series)


def test_aggregate_frame_combinations() -> None:
    def df2frame(val: DataFrame) -> DataFrame:
        return pd.DataFrame(val)

    def df2series(val: DataFrame) -> Series:
        return val.mean()

    def df2scalar(val: DataFrame) -> float:
        return float(val.mean().mean())

    with pytest_warns_bounded(
        FutureWarning,
        r"The provided callable <function (sum|mean) .*> is currently using ",
        lower="2.0.99",
    ):
        check(DF.resample(MonthFreq).aggregate(np.sum), DataFrame)
        check(DF.resample(MonthFreq).aggregate([np.mean]), DataFrame)
        check(DF.resample(MonthFreq).aggregate(["sum", np.mean]), DataFrame)
        check(DF.resample(MonthFreq).aggregate({"col1": np.sum}), DataFrame)
        check(
            DF.resample(MonthFreq).aggregate({"col1": np.sum, "col2": np.mean}),
            DataFrame,
        )
        check(
            DF.resample(MonthFreq).aggregate(
                {"col1": [np.sum], "col2": ["sum", np.mean]}
            ),
            DataFrame,
        )
        check(
            DF.resample(MonthFreq).aggregate(
                {"col1": np.sum, "col2": ["sum", np.mean]}
            ),
            DataFrame,
        )
        check(
            DF.resample(MonthFreq).aggregate({"col1": "sum", "col2": [np.mean]}),
            DataFrame,
        )

    check(DF.resample(MonthFreq).aggregate("sum"), DataFrame)
    check(DF.resample(MonthFreq).aggregate(df2frame), DataFrame)
    check(DF.resample(MonthFreq).aggregate(df2series), DataFrame)
    check(DF.resample(MonthFreq).aggregate(df2scalar), DataFrame)


def test_getitem() -> None:
    check(assert_type(DF.resample(MonthFreq)["col1"], SeriesGroupBy), SeriesGroupBy)
    check(
        assert_type(DF.resample(MonthFreq)[["col1", "col2"]], DataFrameGroupBy),
        DataFrameGroupBy,
    )
