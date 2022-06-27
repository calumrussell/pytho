use pyo3::prelude::*;
use pyo3::types::{PyDict, PyFloat, PyList};
use pyo3::wrap_pyfunction;

use std::collections::HashMap;
use std::io::Error;

use alator::sim::broker::SimulatedBroker;
use alator::broker::{BrokerCost, Quote};
use alator::universe::StaticUniverse;
use alator::data::{CashValue, DataSource, DateTime, PortfolioAllocation, Price};
use alator::perf::PortfolioPerformance;
use alator::sim::portfolio::SimPortfolio;
use alator::simcontext::{PerfResults, SimContext};
use alator::strategy::fixedweight::FixedWeightStrategy;

fn insert_quote(symbol: &str, price: &Price, date: &DateTime, existing: &mut HashMap<DateTime, Vec<Quote>>) {
    let q = Quote {
        symbol: symbol.to_string(),
        bid: *price,
        ask: *price,
        date: *date,
    };

    if existing.contains_key(date) {
        let mut current = existing.get(date).unwrap().to_owned();
        current.push(q);
        existing.insert(date.clone(), current);
    } else {
        existing.insert(date.clone(), vec![q]);
    }
}

fn cum_returns(returns: Vec<f64>) -> Vec<f64> {
    let mut res: Vec<f64> = Vec::new();
    let mut tmp = 1.0;
    let test = 1.0;
    res.push(tmp);
    for i in returns {
        tmp = tmp * (1.0 + (i / 100.0));
        res.push(tmp);
    }
    res
}

#[pyfunction]
fn fixedweight_backtest(
    assets: &PyList,
    weights: &PyDict,
    data: &PyDict,
) -> Result<PerfResults, Error> {
    let assets_r: Vec<&str> = assets.extract()?;
    let weights_r: HashMap<String, f64> = weights.extract()?;
    let data_r: HashMap<i64, HashMap<String, HashMap<i64, f64>>> = data.extract()?;

    let mut raw_data: HashMap<DateTime, Vec<Quote>> = HashMap::new();
    for (asset, prices) in data_r {
        let open: &HashMap<i64, f64> = prices.get(&String::from("Open")).unwrap();
        let close: &HashMap<i64, f64> = prices.get(&String::from("Close")).unwrap(); 
        for (date, price) in open {
            insert_quote(&asset.to_string(), price.into(), date.into(), &mut raw_data);
        }

        for (date, price) in close {
            insert_quote(&asset.to_string(), price.into(), date.into(), &mut raw_data);
        }
    }
    let raw_dividends: HashMap<DateTime, Vec<Dividend>> = HashMap::new();

    let mut weights = PortfolioAllocation::new();
    for symbol in weights_r.keys() {
        weights.insert(&symbol.clone(), &(weights_r.get().unwrap().into()))
    }

    let universe = StaticUniverse::new(assets_r);
    let initial_cash = 100_000.0;

    let dates: Vec<DateTime> = raw_data.keys().cloned().map(|v| v.into()).collect();
    let source = DataSource::from_hashmap(raw_data, raw_dividends);

    let simbrkr = SimulatedBroker::new(source, vec![BrokerCost::Flat(0.001.into())]);
    let port = SimPortfolio::new(simbrkr);

    let perf = PortfolioPerformance::daily();
    let strat = FixedWeightStrategy::new(port, perf, weights);
    let mut sim = SimContext::new(dates, initial_cash.into(), &strat);
    sim.run();
    let perf_res = sim.calculate_perf();
    Ok(perf_res)
}

#[pyfunction]
fn max_dd_threshold_position(
    returns: &PyList,
    threshold: &PyFloat,
) -> Result<Vec<(f64, f64, f64)>, PyErr> {
    /*Finds every drawdown greater than the threshold.
    Drawdown is any period in which the asset drops
    by more than the threshold, until it surpasses the
    peak during that same period.

    If the asset is in a drawdown at the end of the period
    then we should return the last date.

    Returns the scale of the drawdown, and the start
    and end period of the drawdown.
    */

    let returns_r: Vec<f64> = returns.extract()?;
    let threshold_r: f64 = threshold.extract()?;
    let total_returns: Vec<f64> = cum_returns(returns_r);

    let mut peak: f64 = 1.0;
    let mut trough: f64 = 1.0;
    let mut t1: f64 = 0.0;
    let mut t2: f64 = 0.0;
    let mut result_buffer = (0.0, 0.0, 0.0);
    let mut res: Vec<(f64, f64, f64)> = Vec::new();

    for i in 0..total_returns.len() {
        /*Four conditions:
        * We are at a new high coming out of a drawdown,
        therefore the drawdown has ended. We set the drawdown
        end position, and reset the buffer.
        * We are at a new high without a drawdown, we
        reset the start position of drawdown.
        * We are below the peak, but not below the threshold.
        * We are below the peak, and exceed the threshold.
        We record the size of the dd.
        */

        t1 = total_returns[i];
        if t1 > peak {
            if !(result_buffer.2 == 0.0) {
                result_buffer.1 = i as f64;
                if result_buffer.2 < threshold_r {
                    res.push(result_buffer);
                }
                result_buffer = (0.0, 0.0, 0.0);
                result_buffer.0 = i as f64 + 1.0;
                result_buffer.1 = i as f64 + 1.0;
                peak = t1;
                trough = peak;
            } else {
                result_buffer.0 = i as f64 + 1.0;
            }
        } else if t1 < trough {
            trough = t1;
            t2 = (trough / peak) - 1.0;
            if t2 < result_buffer.2 {
                result_buffer.2 = t2;
            }
        }
    }
    Ok(res)
}

#[pymodule]
fn rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(fixedweight_backtest, m)?)
        .unwrap();
    m.add_function(wrap_pyfunction!(max_dd_threshold_position, m)?)
        .unwrap();
    Ok(())
}
