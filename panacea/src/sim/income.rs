use super::common::insert_quote;

use std::collections::HashMap;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyFloat, PyList};
use antevorta::country::uk::{UKIncome, UKSimulationBuilder, UKSimulationResult, NIC};
use antevorta::schedule::Schedule;
use antevorta::sim::Simulation;
use antevorta::strat::StaticInvestmentStrategy;
use alator::sim::portfolio::SimPortfolio;
use alator::sim::broker::SimulatedBroker;
use alator::data::{DataSource, DateTime, PortfolioAllocation, Price};
use alator::broker::{BrokerCost, Dividend, Quote};

type PySimResults = (f64, f64, f64, f64);

fn convert_sim_results(res: UKSimulationResult) -> PySimResults {
    (res.cash.into(), res.isa.into(), res.gia.into(), res.sipp.into())
}

#[pyfunction]
pub fn income_simulation(
    assets: &PyList,
    weights: &PyDict,
    data: &PyDict,
    initial_cash: &PyFloat,
    income_value: &PyFloat,
    income_growth: &PyFloat
) -> PyResult<PySimResults> {
    let sim_start = 10.into();
    const SIM_LENGTH: i64 = 100;

    let assets_r: Vec<&str> = assets.extract()?;
    let weights_r: HashMap<String, f64> = weights.extract()?;
    let data_r: HashMap<i64, HashMap<String, HashMap<i64, f64>>> = data.extract()?;

    let mut raw_data: HashMap<DateTime, Vec<Quote>> = HashMap::new();
    for (asset, prices) in data_r {
        let open: &HashMap<i64, f64> = prices.get(&String::from("Open")).unwrap();
        let close: &HashMap<i64, f64> = prices.get(&String::from("Close")).unwrap(); 

        for (date, price) in open {
            let p: Price = (*price).into();
            let d: DateTime = (*date).into();
            insert_quote(&asset.to_string(), &p, &d, &mut raw_data);
        }

        for (date, price) in close {
            let p: Price = (*price).into();
            let d: DateTime = (*date).into();
            insert_quote(&asset.to_string(), &p, &d, &mut raw_data);
        }
    }
    let raw_dividends: HashMap<DateTime, Vec<Dividend>> = HashMap::new();
    let source = DataSource::from_hashmap(raw_data, raw_dividends);

    let mut weights = PortfolioAllocation::new();
    for symbol in weights_r.keys() {
        weights.insert(&symbol.clone(), &(*weights_r.get(&symbol.clone()).unwrap()).into())
    }
 
    let brokercosts = vec![BrokerCost::PctOfValue(0.005)];
    let simbrkr = SimulatedBroker::new(source, brokercosts);
    let port = SimPortfolio::new(simbrkr);
    let ia = StaticInvestmentStrategy::new(Schedule::EveryFriday, weights);

    let income_g: f64 = income_growth.extract()?;
    let growth: f64 = (1.0 + income_g).powf(1.0 / 12.0);
    let cash: f64 = initial_cash.extract()?;
    let income: f64 = income_value.extract()?;

    let mut state_builder = UKSimulationBuilder::new(cash.into(), 0.0.into(), NIC::A, ia, port);
    let employment = UKIncome::Employment(income.into(), Schedule::EveryMonth(25))
        .with_fixedrate_growth(&sim_start, &SIM_LENGTH, &growth);
    state_builder.add_incomes(employment);
    let mut state = state_builder.build();

    let mut sim = Simulation {
        start_date: sim_start,
        length: SIM_LENGTH,
    };
    let result = sim.run(&mut state);
    Ok(convert_sim_results(result.get_perf()))
}
