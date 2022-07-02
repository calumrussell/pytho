use alator::broker::{BrokerCost, Dividend, Quote};
use alator::data::{DataSource, DateTime, PortfolioAllocation};
use alator::sim::broker::SimulatedBroker;
use alator::sim::portfolio::SimPortfolio;
use antevorta::country::uk::{UKIncome, UKSimulationBuilder, UKSimulationResult, NIC};
use antevorta::schedule::Schedule;
use antevorta::sim::Simulation;
use antevorta::strat::StaticInvestmentStrategy;
use pyo3::prelude::*;
use std::collections::HashMap;

#[pyclass]
#[derive(Clone)]
pub struct IncomeInput {
    pub assets: Vec<String>,
    pub weights: HashMap<String, f64>,
    pub dates: Vec<i64>,
    pub close: HashMap<String, Vec<f64>>,
    pub initial_cash: f64,
    pub wage: f64,
    //TODO: especially bad name, needs to change
    pub income_growth: f64,
}

#[pymethods]
impl IncomeInput {
    #[new]
    fn new(
        assets: Vec<String>,
        weights: HashMap<String, f64>,
        dates: Vec<i64>,
        close: HashMap<String, Vec<f64>>,
        initial_cash: f64,
        wage: f64,
        income_growth: f64,
    ) -> Self {
        IncomeInput {
            assets,
            weights,
            dates,
            close,
            initial_cash,
            wage,
            income_growth,
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
pub fn income_simulation(input: &IncomeInput) -> PyResult<PySimResults> {
    let start_date = input.dates.first().unwrap().clone();
    let sim_len = input.dates.len();

    let mut raw_data: HashMap<DateTime, Vec<Quote>> = HashMap::new();
    for pos in 0..sim_len {
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
    let source = DataSource::from_hashmap(raw_data, raw_dividends);

    let mut weights = PortfolioAllocation::new();
    for symbol in input.weights.keys() {
        weights.insert(
            &symbol.clone(),
            &(*input.weights.get(&symbol.clone()).unwrap()).into(),
        )
    }

    let brokercosts = vec![BrokerCost::PctOfValue(0.005)];
    let simbrkr = SimulatedBroker::new(source, brokercosts);
    let port = SimPortfolio::new(simbrkr);
    let ia = StaticInvestmentStrategy::new(Schedule::EveryFriday, weights);

    let growth: f64 = (1.0 + input.income_growth).powf(1.0 / 12.0);
    let mut state_builder = UKSimulationBuilder::new(input.initial_cash.into(), 0.0.into(), NIC::A, ia, port);
    let employment = UKIncome::Employment(input.wage.into(), Schedule::EveryMonth(25))
        .with_fixedrate_growth(&start_date.into(), &(sim_len as i64), &growth);
    state_builder.add_incomes(employment);
    let mut state = state_builder.build();

    let mut sim = Simulation {
        start_date: start_date.into(),
        length: sim_len as i64,
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

    use super::{income_simulation, IncomeInput};

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
                IncomeInput {
                    dates,
                    assets,
                    close,
                    weights,
                    initial_cash: 100_000.0,
                    wage: 4_000.0,
                    income_growth: 0.02,
                },
            )
            .unwrap()
            .borrow();
            let res = income_simulation(&obj);
            println!("{:?}", res.unwrap());
            Ok(())
        });
    }
}
