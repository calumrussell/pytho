import React from 'react';
import axios from 'axios';

import {
  useMessage,
} from '@Components/reducers/message';

const initialState = {
  results: undefined, 
};

const actionTypes = {
  simComplete: 'SIM_END',
  simClear: 'SIM_CLR',
};

const reducer = (state, action) => {
  switch (action.type) {
    case actionTypes.simComplete: {
      return {
        results: action.results
      }
    }
    case actionTypes.simClear: {
      return {
        results: undefined
      }
    }
    default: {
      new Error('Unknown action type');
    }
  }
};

const AntevortaContext = React.createContext();

export const useAntevorta = () => {
  const context = React.useContext(AntevortaContext);
  const {
    state, dispatch,
  } = context;

  const {
    errorMessage
  } = useMessage();

  const simComplete = (results) => dispatch({
    type: 'SIM_END',
    results,
  });
  const clearSim = () => dispatch({
    type: 'SIM_CLR',
  });

  const simInputBuilder = (portfolio, initialCash, wage, wageGrowth) => ({
    "data": {
      "initial_cash": Number(initialCash),
      "wage": Number(wage),
      "wage_growth": wageGrowth / 100.0,
      ...portfolio.portfolio.toPost()
    }
  });

  const runSim = (simInput, finallyFunc) => {
    axios.post(process.env.API_URL + `/api/incomesim`, simInput)
      .then((res) => res.data)
      .then((res) => simComplete(res.data))
      .catch((err) => {
          if (err.response) {
            errorMessage(err.response.data.message);
          }
        })
      .finally(finallyFunc);
  };

  return {
    state,
    runSim,
    simInputBuilder,
    clearSim,
  };
};

export const AntevortaProvider = (props) => {
  const [
    state,
    dispatch,
  ] = React.useReducer(reducer, initialState);
  return <AntevortaContext.Provider
    value={
      {
        state,
        dispatch,
      }
    }
    { ...props } />;
};
