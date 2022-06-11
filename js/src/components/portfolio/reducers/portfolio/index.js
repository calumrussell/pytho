import React from 'react';

import {
  weightedPortfolio,
} from '@Components/portfolio/helpers/portfolio';

const initialState = {
  portfolio: null,
  isEmpty: true,
};

const actionTypes = {
  addToPortfolio: 'ADD_PORTFOLIO',
  removeFromPortfolio: 'REMOVE_PORTFOLIO',
  loadPortfolio: 'LOAD_PORTFOLIO',
};

const reducer = (state, action) => {
  switch (action.type) {
    case actionTypes.addToPortfolio:
      if (state.portfolio != null) {
        const newWs = state.portfolio.getCopy();
        newWs.addAsset(action.asset, action.weight);
        return {
          ...state,
          portfolio: newWs,
        };
      } else {
        const ws = weightedPortfolio();
        ws.addAsset(action.asset, action.weight);
        return {
          ...state,
          portfolio: ws,
          isEmpty: false,
        };
      }
    case actionTypes.removeFromPortfolio:
      const copy = {
        ...state.portfolio,
      };
      copy.removeAsset(action.index);
      return {
        ...state,
        portfolio: copy,
        isEmpty: copy.getLength() === 0,
      };
    case actionTypes.loadPortfolio:
      const newPortCopy = {
        ...action.portfolio,
      };
      return {
        ...state,
        portfolio: newPortCopy,
        isEmpty: newPortCopy.getLength() === 0,
      };
    default:
      new Error('Unknown action type');
  }
};

const PortfolioContext = React.createContext();

export const usePortfolio = () => {
  const context = React.useContext(PortfolioContext);
  const {
    state, dispatch,
  } = context;

  const addToPortfolio = (asset, weight) => dispatch({
    type: 'ADD_PORTFOLIO',
    asset,
    weight,
  });

  const removeFromPortfolio = (index) => dispatch({
    type: 'REMOVE_PORTFOLIO',
    index,
  });

  const hasPortfolio = () => state.portfolio != null;

  const loadPortfolioFromUser = (portfolio) => dispatch({
    type: 'LOAD_PORTFOLIO',
    portfolio,
  });

  return {
    state,
    loadPortfolioFromUser,
    hasPortfolio,
    addToPortfolio,
    removeFromPortfolio,
  };
};

export const PortfolioProvider = (props) => {
  const [
    state,
    dispatch,
  ] = React.useReducer(reducer, initialState);
  return <PortfolioContext.Provider
    value={
      {
        state,
        dispatch,
      }
    }
    { ...props } />;
};

