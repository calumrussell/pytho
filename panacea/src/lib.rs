pub mod calcs;
pub mod sim;

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

#[pymodule]
fn panacea(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<sim::BacktestInput>()?;
    m.add_class::<sim::IncomeInput>()?;
    m.add_function(wrap_pyfunction!(sim::income_simulation, m)?)
        .unwrap();
    m.add_function(wrap_pyfunction!(sim::fixedweight_backtest, m)?)
        .unwrap();
    m.add_function(wrap_pyfunction!(calcs::max_dd_threshold_position, m)?)
        .unwrap();
    Ok(())
}
