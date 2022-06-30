use std::collections::HashMap;
use alator::data::{DateTime, Price};
use alator::broker::Quote;

pub fn insert_quote(symbol: &str, price: &Price, date: &DateTime, existing: &mut HashMap<DateTime, Vec<Quote>>) {
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
