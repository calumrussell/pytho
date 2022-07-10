use crate::stat::build_sample_raw_daily;
use alator::broker::{BrokerCost, Dividend, Quote};
use alator::data::{DataSource, DateTime, PortfolioAllocation};
use alator::sim::broker::SimulatedBroker;
use alator::sim::portfolio::SimPortfolio;
use antevorta::country::uk::{
    UKIncome, UKSimulationBuilder, UKSimulationBuilderConfig, UKSimulationResult, NIC,
};
use antevorta::schedule::Schedule;
use antevorta::sim::Simulation;
use antevorta::strat::StaticInvestmentStrategy;
use pyo3::create_exception;
use pyo3::exceptions::PyException;
use pyo3::prelude::*;
use std::collections::HashMap;

create_exception!(
    panacea,
    InsufficientDataError,
    PyException,
    "Insufficient data to resample."
);

#[pyclass]
#[derive(Clone, Debug)]
pub struct AntevortaBasicInput {
    pub assets: Vec<String>,
    pub weights: HashMap<String, f64>,
    pub dates: Vec<i64>,
    pub close: HashMap<String, Vec<f64>>,
    pub initial_cash: f64,
    pub wage: f64,
    pub wage_growth: f64,
    pub contribution_pct: f64,
    pub emergency_cash_min: f64,
    pub sim_length: i64,
}

#[pymethods]
impl AntevortaBasicInput {
    #[new]
    fn new(
        assets: Vec<String>,
        weights: HashMap<String, f64>,
        dates: Vec<i64>,
        close: HashMap<String, Vec<f64>>,
        initial_cash: f64,
        wage: f64,
        wage_growth: f64,
        contribution_pct: f64,
        emergency_cash_min: f64,
        sim_length: i64,
    ) -> Self {
        AntevortaBasicInput {
            assets,
            weights,
            dates,
            close,
            initial_cash,
            wage,
            wage_growth,
            contribution_pct,
            emergency_cash_min,
            sim_length,
        }
    }
}

type PySimResults = (f64, f64, f64, f64);

fn convert_sim_results(res: UKSimulationResult) -> PySimResults {
    (
        res.cash.into(),
        res.isa.into(),
        res.gia.into(),
        res.sipp.into(),
    )
}

#[pyfunction]
pub fn antevorta_basic(input: &AntevortaBasicInput) -> PyResult<PySimResults> {
    let start_date = input.dates.first().unwrap().clone();

    let mut raw_data: HashMap<DateTime, Vec<Quote>> = HashMap::new();
    if let Some(resampled_close) = build_sample_raw_daily(input.sim_length, input.close.clone()) {
        let sim_length_days = input.sim_length * 365;
        let mut iter_date = input.dates.first().unwrap().clone();
        //The simulator builds its own dates to use an input
        //This will iterate over the prices within the resampled_close, therefore the vectors have to
        //be equal to sim_length_days
        for pos in 0..sim_length_days {
            let mut quotes: Vec<Quote> = Vec::new();
            for asset in &input.assets {
                let asset_closes = resampled_close.get(asset).unwrap();
                let pos_close = asset_closes[pos as usize];
                let q = Quote {
                    date: iter_date.into(),
                    bid: pos_close.into(),
                    ask: pos_close.into(),
                    symbol: asset.clone(),
                };
                quotes.push(q);
            }
            raw_data.insert(iter_date.into(), quotes);
            //Add one day in seconds
            iter_date += 84600;
        }
    } else {
        return Err(InsufficientDataError::new_err("Insufficient data"));
    }
    let raw_dividends: HashMap<DateTime, Vec<Dividend>> = HashMap::new();
    let source = DataSource::from_hashmap(raw_data, raw_dividends);

    let mut weights = PortfolioAllocation::new();
    for symbol in input.weights.keys() {
        weights.insert(
            &symbol.clone(),
            &(*input.weights.get(&symbol.clone()).unwrap()).into(),
        )
    }

    let brokercosts = vec![BrokerCost::Flat(0.01.into())];
    let simbrkr = SimulatedBroker::new(source, brokercosts);
    let port = SimPortfolio::new(simbrkr);
    let ia = StaticInvestmentStrategy::new(Schedule::EveryFriday, weights);

    let growth: f64 = (1.0 + input.wage_growth).powf(1.0 / 12.0) - 1.0;
    let config = UKSimulationBuilderConfig {
        start_cash: input.initial_cash.into(),
        lifetime_pension_contributions: 0.0.into(),
        contribution_pct: input.contribution_pct,
        emergency_cash_min: input.emergency_cash_min.into(),
        nic: NIC::A,
        portfolio: port,
        strat: ia,
    };
    let mut state_builder = UKSimulationBuilder::new(config);
    let employment = UKIncome::Employment(input.wage.into(), Schedule::EveryMonth(25))
        .with_fixedrate_growth(&start_date.into(), &(input.sim_length * 365), &growth);
    state_builder.add_incomes(employment);
    let mut state = state_builder.build();

    let mut sim = Simulation {
        start_date: start_date.into(),
        length: input.sim_length * 365,
    };
    let result = sim.run(&mut state);
    Ok(convert_sim_results(result.get_perf()))
}

#[cfg(test)]
mod tests {

    use std::collections::HashMap;

    use pyo3::prelude::*;
    use rand::distributions::Uniform;
    use rand::{thread_rng, Rng};
    use rand_distr::{Distribution, Normal};

    use super::{antevorta_basic, AntevortaBasicInput};

    #[test]
    fn run_income() {
        //Weights is {symbol: weight}
        //Data is {asset_id[i64]: {Open/Close[str]: {date[i64], price[f64]}}}
        let price_dist = Uniform::new(1.0, 100.0);
        let vol_dist = Uniform::new(0.1, 0.2);
        let mut rng = thread_rng();
        let price = rng.sample(price_dist);
        let vol = rng.sample(vol_dist);
        let ret_dist = Normal::new(0.0, vol).unwrap();

        let assets = vec![0.to_string(), 1.to_string()];
        let dates: Vec<i64> = (0..500).collect();
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
                AntevortaBasicInput {
                    dates,
                    assets,
                    close,
                    weights,
                    initial_cash: 100_000.0,
                    wage: 4_000.0,
                    wage_growth: 0.02,
                    contribution_pct: 0.10,
                    emergency_cash_min: 5_000.0,
                    sim_length: 20,
                },
            )
            .unwrap()
            .borrow();
            let res = antevorta_basic(&obj);
            println!("{:?}", res.unwrap());
            Ok(())
        });
    }
}
