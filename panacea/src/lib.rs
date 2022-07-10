pub mod calcs;
pub mod sim;
pub mod stat;

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

#[pymodule]
fn panacea(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<sim::AlatorInput>()?;
    m.add_class::<sim::AntevortaBasicInput>()?;
    m.add(
        "InsufficientDataError",
        py.get_type::<sim::InsufficientDataError>(),
    )?;
    m.add_function(wrap_pyfunction!(sim::alator_backtest, m)?)
        .unwrap();
    m.add_function(wrap_pyfunction!(sim::antevorta_basic, m)?)
        .unwrap();
    m.add_function(wrap_pyfunction!(calcs::max_dd_threshold_position, m)?)
        .unwrap();
    Ok(())
}
