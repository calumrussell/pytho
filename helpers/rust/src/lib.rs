use pyo3::prelude::*;
use pyo3::types::{PyDict, PyFloat, PyList};
use pyo3::wrap_pyfunction;

use std::collections::HashMap;
use std::io::Error;

use alator::sim::broker::SimulatedBroker;
use alator::broker::Quote;
use alator::universe::{DefinedUniverse, StaticUniverse};
use alator::data::DataSource;
use alator::perf::PortfolioPerformance;
use alator::sim::portfolio::SimPortfolio;
use alator::simcontext::SimContext;
use alator::strategy::staticweight::StaticWeightStrategyRulesMonthlyRebalancing;
use alator::strategy::fixedweight::FixedWeightStrategy;

fn insert_quote(symbol: &String, price: &f64, date: &i64, existing: &mut HashMap<i64, Vec<Quote>>) {
    let q = Quote {
        symbol: symbol.to_owned(),
        bid: price.to_owned(),
        ask: price.to_owned(),
        date: date.to_owned(),
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
fn staticweight_backtest(
    weights_py: &PyList,
    sample_prices_py: &PyList,
) -> Result<(f64, f64, f64, f64, f64, Vec<f64>, Vec<f64>, Vec<i64>), PyErr> {
    let initial_cash = 100.00;
    let weights_r: Vec<Vec<f64>> = weights_py.extract()?;
    let sample_prices_r: Vec<Vec<f64>> = sample_prices_py.extract()?;

    let mut raw_data: HashMap<i64, Vec<Quote>> = HashMap::new();
    for (i, price_row) in sample_prices_r.iter().enumerate() {
        let mut temp: Vec<Quote> = Vec::new();
        let date = (i + 1) as i64;
        for (j, price) in price_row.iter().enumerate() {
            temp.push(Quote {
                bid: price.clone(),
                ask: price.clone(),
                symbol: j.to_string(),
                date: date,
            });
        }
        raw_data.insert(date, temp);
    }
    let dates = raw_data.keys().map(|d| d.clone()).collect();

    let universe_vec_str: Vec<String> = (0..weights_r.len()).map(|v| v.to_string()).collect();
    let universe_vec_ptr: Vec<&str> = universe_vec_str.iter().map(String::as_str).collect();
    let universe = StaticUniverse::new(universe_vec_ptr);

    let mut weights: Vec<HashMap<String, f64>> = Vec::new();
    for weight_r_row in weights_r {
        let mut temp: HashMap<String, f64> = HashMap::new();
        for (weight, asset) in weight_r_row.iter().zip(universe.get_assets()) {
            temp.insert(asset.clone(), weight.clone());
        }
        weights.push(temp);
    }

    let source = DataSource::from_hashmap(raw_data);

    let simbrkr = SimulatedBroker::new(source);
    let port = SimPortfolio::new(simbrkr);

    let perf = PortfolioPerformance::daily();
    let strat = StaticWeightStrategyRulesMonthlyRebalancing::new(port, perf, weights);
    let mut sim = SimContext::new(dates, initial_cash, &strat);
    sim.run();
    let perf_res = sim.calculate_perf();
    Ok(perf_res)
}

#[pyfunction]
fn fixedweight_backtest(
    assets: &PyList,
    weights: &PyDict,
    data: &PyDict,
) -> Result<(f64, f64, f64, f64, f64, Vec<f64>, Vec<f64>, Vec<i64>), Error> {
    let assets_r: Vec<&str> = assets.extract()?;
    let weights_r: HashMap<String, f64> = weights.extract()?;
    let data_r: HashMap<i64, HashMap<String, HashMap<i64, f64>>> = data.extract()?;

    let mut raw_data: HashMap<i64, Vec<Quote>> = HashMap::new();
    for (asset, prices) in data_r {
        let open: &HashMap<i64, f64> = prices.get(&String::from("Open")).unwrap();
        let close: &HashMap<i64, f64> = prices.get(&String::from("Close")).unwrap();

        for (date, price) in open {
            insert_quote(&asset.to_string(), price, date, &mut raw_data);
        }

        for (date, price) in close {
            insert_quote(&asset.to_string(), price, date, &mut raw_data);
        }
    }

    let universe = StaticUniverse::new(assets_r);
    let initial_cash = 1e5;

    let dates = raw_data.keys().map(|d| d.clone()).collect();

    let source = DataSource::from_hashmap(raw_data);

    let simbrkr = SimulatedBroker::new(source);
    let port = SimPortfolio::new(simbrkr);

    let perf = PortfolioPerformance::daily();
    let strat = FixedWeightStrategy::new(port, perf, weights_r);
    let mut sim = SimContext::new(dates, initial_cash, &strat);
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
    m.add_function(wrap_pyfunction!(staticweight_backtest, m)?)
        .unwrap();
    m.add_function(wrap_pyfunction!(max_dd_threshold_position, m)?)
        .unwrap();
    Ok(())
}
