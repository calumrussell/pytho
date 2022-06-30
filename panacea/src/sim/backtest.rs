use alator::broker::{BrokerCost, Dividend, Quote};
use alator::data::{DataSource, DateTime, PortfolioAllocation};
use alator::perf::{PerfStruct, PortfolioPerformance};
use alator::sim::broker::SimulatedBroker;
use alator::sim::portfolio::SimPortfolio;
use alator::simcontext::SimContext;
use alator::strategy::fixedweight::FixedWeightStrategy;
use pyo3::prelude::*;
use std::collections::HashMap;

#[pyclass]
#[derive(Clone)]
pub struct BacktestInput {
    pub assets: Vec<String>,
    pub weights: HashMap<String, f64>,
    pub dates: Vec<i64>,
    pub close: HashMap<String, Vec<f64>>,
}

#[pymethods]
impl BacktestInput {
    #[new]
    fn new(
        assets: Vec<String>,
        weights: HashMap<String, f64>,
        dates: Vec<i64>,
        close: HashMap<String, Vec<f64>>,
    ) -> Self {
        BacktestInput {
            assets,
            weights,
            dates,
            close,
        }
    }
}

type PyPerfResults = (f64, f64, f64, f64, f64, Vec<f64>, Vec<f64>, Vec<f64>);

fn convert_result(res: PerfStruct) -> PyPerfResults {
    (
        res.ret,
        res.cagr,
        res.vol,
        res.mdd,
        res.sharpe,
        res.values,
        res.returns,
        res.dates,
    )
}

#[pyfunction]
pub fn fixedweight_backtest(input: &BacktestInput) -> PyResult<PyPerfResults> {
    let data_len = input.dates.len();

    let mut raw_data: HashMap<DateTime, Vec<Quote>> = HashMap::new();
    for pos in 0..data_len {
        let curr_date: DateTime = input.dates[pos].into();
        let mut quotes: Vec<Quote> = Vec::new();
        for asset in &input.assets {
            let close = input.close.get(asset).unwrap();
            let q = Quote {
                date: curr_date,
                bid: close[pos].into(),
                ask: close[pos].into(),
                symbol: asset.clone(),
            };
            quotes.push(q);
        }
        raw_data.insert(curr_date, quotes);
    }
    let raw_dividends: HashMap<DateTime, Vec<Dividend>> = HashMap::new();

    let mut weights = PortfolioAllocation::new();
    for symbol in input.weights.keys() {
        weights.insert(
            &symbol.clone(),
            &(*input.weights.get(&symbol.clone()).unwrap()).into(),
        )
    }

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
    Ok(convert_result(perf_res))
}

#[cfg(test)]
mod tests {

    use std::collections::HashMap;

    use pyo3::prelude::*;
    use rand::distributions::Uniform;
    use rand::{thread_rng, Rng};
    use rand_distr::{Distribution, Normal};

    use super::{fixedweight_backtest, BacktestInput};

    #[test]
    fn run_backtest() {
        //Weights is {symbol: weight}
        //Data is {asset_id[i64]: {Open/Close[str]: {date[i64], price[f64]}}}
        let price_dist = Uniform::new(1.0, 100.0);
        let vol_dist = Uniform::new(0.1, 0.2);
        let mut rng = thread_rng();
        let price = rng.sample(price_dist);
        let vol = rng.sample(vol_dist);
        let ret_dist = Normal::new(0.0, vol).unwrap();

        let assets = vec![0.to_string(), 1.to_string()];
        let dates: Vec<i64> = (0..100).collect();
        let mut close: HashMap<String, Vec<f64>> = HashMap::new();
        for asset in &assets {
            let mut close_data: Vec<f64> = Vec::new();
            for _date in &dates {
                let period_ret = ret_dist.sample(&mut rng);
                let new_price = price * (1.0 + period_ret);
                close_data.push(new_price);
            }
            close.insert(asset.clone(), close_data);
        }

        let mut weights: HashMap<String, f64> = HashMap::new();
        weights.insert(String::from("0"), 0.5);
        weights.insert(String::from("1"), 0.5);

        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| -> PyResult<()> {
            let obj = PyCell::new(
                py,
                BacktestInput {
                    dates,
                    assets,
                    close,
                    weights,
                },
            )
            .unwrap()
            .borrow();
            let res = fixedweight_backtest(&obj);
            println!("{:?}", res.unwrap());
            Ok(())
        });
    }
}
