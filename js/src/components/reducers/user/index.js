import React from 'react';

import {
  useMessage,
} from '@Components/reducers/message';

const initialState = {
  portfolios: {},
};

const actionTypes = {
  savePortfolio: 'SAVE_PORTFOLIO',
};

const reducer = (state, action) => {
  switch (action.type) {
    case actionTypes.savePortfolio:

      const portCopy = action.portfolio.getCopy();

      const copy = {
        ...state.portfolios,
      };
      copy[action.name] = portCopy;
      return {
        ...state,
        portfolios: copy,
      };

    default:
      new Error('Unknown action type');
  }
};

const UserContext = React.createContext();

export const useUser = () => {
  const context = React.useContext(UserContext);
  const {
    state, dispatch,
  } = context;
  const {
    successMessage,
  } = useMessage();

  const savePortfolio = (portfolio, name) => {
    if (name in state.portfolios) {
      successMessage('Overwriting portfolio');
    }
    dispatch({
      type: 'SAVE_PORTFOLIO',
      portfolio,
      name,
    });
  };

  const getPortfolioByName = (name) => state.portfolios[name];
  const getPortfolioNames = () => Object.keys(state.portfolios);
  const userHasPortfolios = () => getPortfolioNames().length > 0;

  return {
    state,
    getPortfolioByName,
    getPortfolioNames,
    userHasPortfolios,
    savePortfolio,
  };
};

export const UserProvider = (props) => {
  const [
    state,
    dispatch,
  ] = React.useReducer(reducer, initialState);
  return <UserContext.Provider
    value={
      {
        state,
        dispatch,
      }
    }
    { ...props } />;
};
