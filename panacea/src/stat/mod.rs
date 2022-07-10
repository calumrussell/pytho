use std::collections::HashMap;

use alator::broker::Quote;
use alator::data::DateTime;
use rand::distributions::Uniform;
use rand::thread_rng;
use rand_distr::Distribution;

pub fn build_sample(
    start_date: i64,
    sim_length_yrs: i64,
    raw_data: HashMap<DateTime, Vec<Quote>>,
    dates: &Vec<i64>,
) -> Option<HashMap<DateTime, Vec<Quote>>> {
    //Check that data is long enough for resampling
    let data_length = dates.len() as i64;
    const DAYS_IN_YEAR: i64 = 365;
    if data_length < DAYS_IN_YEAR {
        return None;
    }

    //If it is, then sample sim_length_yrs number of values from uniform distribution
    //from 0 to length of data - 365
    let sim_length_dist = Uniform::new(0, data_length - DAYS_IN_YEAR);
    let mut rng = thread_rng();
    let mut sample_start_positions: Vec<i64> = Vec::new();
    for _sample_period in 0..sim_length_yrs {
        let sample_pos = sim_length_dist.sample(&mut rng);
        sample_start_positions.push(sample_pos as i64);
    }
    //Then take those samples from the data
    let mut temp_data: Vec<Vec<Quote>> = Vec::new();
    for start_pos in &sample_start_positions {
        let end_pos = *start_pos + DAYS_IN_YEAR;
        for date_pos in *start_pos..end_pos {
            let temp = dates[date_pos as usize];
            let date_quotes = raw_data.get(&temp.into()).unwrap();
            temp_data.push(date_quotes.to_vec());
        }
    }
    //Then restructure back into raw_data format so that it can be used by the simulator
    let mut sim_date = start_date.clone();
    const SECS_IN_DAY: i64 = 86400;

    let mut res: HashMap<DateTime, Vec<Quote>> = HashMap::new();
    for quotes in temp_data {
        res.insert(sim_date.into(), quotes);
        sim_date += SECS_IN_DAY;
    }
    Some(res)
}

#[cfg(test)]
mod tests {
    use alator::broker::Quote;
    use alator::data::DateTime;
    use rand::distributions::Uniform;
    use rand::thread_rng;
    use rand_distr::Distribution;
    use std::collections::HashMap;

    use super::build_sample;

    #[test]
    fn test_sample_generator() {
        let price_dist = Uniform::new(98.0, 102.0);
        let mut rng = thread_rng();

        let mut raw_data: HashMap<DateTime, Vec<Quote>> = HashMap::new();
        let mut fake_dates: Vec<i64> = Vec::new();
        for date in 1..400 {
            let price = price_dist.sample(&mut rng);
            let quote = Quote {
                bid: price.into(),
                ask: price.into(),
                date: date.into(),
                symbol: "ABC".to_string(),
            };
            raw_data.insert(date.into(), vec![quote]);
            fake_dates.push(date);
        }
        let res = build_sample(1, 10, raw_data, &fake_dates);
        let new_sample_len = res.unwrap().keys().len();
        assert!(new_sample_len == 3650);
    }

    #[test]
    fn test_sample_generator_with_insufficient_data() {
        let price_dist = Uniform::new(98.0, 102.0);
        let mut rng = thread_rng();

        let mut raw_data: HashMap<DateTime, Vec<Quote>> = HashMap::new();
        let mut fake_dates: Vec<i64> = Vec::new();
        for date in 1..10 {
            let price = price_dist.sample(&mut rng);
            let quote = Quote {
                bid: price.into(),
                ask: price.into(),
                date: date.into(),
                symbol: "ABC".to_string(),
            };
            raw_data.insert(date.into(), vec![quote]);
            fake_dates.push(date);
        }
        let res = build_sample(1, 10, raw_data, &fake_dates);
        assert!(res.is_none() == true);
    }
}
