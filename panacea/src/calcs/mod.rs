use pyo3::prelude::*;
use pyo3::types::{PyFloat, PyList};

fn cum_returns(returns: Vec<f64>) -> Vec<f64> {
    let mut res: Vec<f64> = Vec::new();
    let mut tmp = 1.0;
    res.push(tmp);
    for i in returns {
        tmp = tmp * (1.0 + (i / 100.0));
        res.push(tmp);
    }
    res
}

#[pyfunction]
pub fn max_dd_threshold_position(
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

#[cfg(test)]
mod tests {

    use pyo3::prelude::*;
    use pyo3::types::{PyFloat, PyList};

    use super::max_dd_threshold_position;

    #[test]
    fn run_threshold() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let rets = PyList::new(py, vec![0.1, -0.1, 0.2, 0.3, -0.15]);
            max_dd_threshold_position(rets, PyFloat::new(py, 0.05));
        });
    }
}
