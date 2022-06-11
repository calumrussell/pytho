import React from 'react';
import axios from 'axios';

import {
  useMessage,
} from '@Components/reducers/message';

const initialState = {
  ticker: null,
  prices: null,
  fundies: null,
  summary: null,
  earnings: null,
};

const actionTypes = {
  addStockData: 'ADD_STOCK_DATA',
  clearStockData: 'CLR_STOCK_DATA',
};

const reducer = (state, action) => {
  switch (action.type) {
    case actionTypes.addStockData:
      return {
        ...state,
        prices: action.prices,
        fundies: action.fundies,
        ticker: action.ticker,
        summary: action.summary,
        earnings: action.earnings,
      };
    case actionTypes.clearStockData:
      return {
        ...state,
        prices: null,
        fundies: null,
        ticker: null,
        summary: null,
        earnings: null,
      };
    default:
      throw Error('Action type not supported');
  }
};

const StockOverviewContext = React.createContext();

export const useStockOverview = () => {
  const context = React.useContext(StockOverviewContext);
  const {
    state, dispatch,
  } = context;

  const {
    errorMessage,
  } = useMessage();

  const getOverview = (ticker) => {
    if (state.summary) {
      dispatch({
        type: 'CLR_STOCK_DATA',
      });
    }

    const priceUrl = `/api/hermesdailyprice?ticker=${ticker}`;
    const fundiesUrl = `/api/hermesfundamentals?ticker=${ticker}`;
    const summaryUrl = `/api/hermessummary?ticker=${ticker}`;
    const earningsUrl = `/api/hermesearnings?ticker=${ticker}`;
    const reqs = [
      priceUrl,
      fundiesUrl,
      summaryUrl,
      earningsUrl,
    ];

    return axios.all(reqs.map((r) => axios.get(process.env.API_URL + r)))
        .then((r) => dispatch({
          type: 'ADD_STOCK_DATA',
          prices: r[0].data,
          fundies: r[1].data,
          summary: r[2].data,
          earnings: r[3].data,
          ticker,
        }))
        .catch((err) => {
          if (err.response) {
            errorMessage(err.response.data.message);
          }
        });
  };

  return {
    state,
    getOverview,
  };
};

export const StockOverviewProvider = (props) => {
  const [
    state,
    dispatch,
  ] = React.useReducer(reducer, initialState);
  return <StockOverviewContext.Provider
    value={
      {
        state,
        dispatch,
      }
    }
    { ...props } />;
};
