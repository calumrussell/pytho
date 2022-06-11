import React from 'react';
import axios from 'axios';

const initialState = {
  securitySearch: '',
  securityType: 'fund',
  securitiesOptions: [
  ],
  securityTypes: [
    'fund',
    'etf',
    'stock',
    'index',
    'factor',
  ],
  requestController: undefined,
};

const actionTypes = {
  clearInput: 'CLEAR_INPUT',
  clearOptions: 'CLEAR_OPTS',
  selectSecurityType: 'SEL_SECTYPE',
  searchSecurity: 'SEARCH_SEC',
  inputSecurity: 'INPUT_SEC',
  requestStart: 'REQ_START',
  requestClear: 'REQ_CLEAR',
};

const reducer = (state, action) => {
  switch (action.type) {
    case actionTypes.clearOptions:
      return {
        ...state,
        securitiesOptions: [
        ],
      };

    case actionTypes.selectSecurityType:
      return {
        ...state,
        securityType: action.securityType,
      };

    case actionTypes.searchSecurity:
      // Only update if the results are for the input
      // that is currently
      if (action.inputString == state.securitySearch) {
        return {
          ...state,
          securitiesOptions: action.options,
        };
      } else {
        return {
          ...state,
        };
      };

    case actionTypes.inputSecurity:
      return {
        ...state,
        securitySearch: action.input,
      };

    case actionTypes.clearInput:
      return {
        ...state,
        securitySearch: '',
      };

    case actionTypes.requestStart:
      return {
        ...state,
        requestController: action.controller,
      };

    case actionTypes.requestClear:
      return {
        ...state,
        requestController: undefined,
      };

    default:
      new Error('Unknown action type');
  }
};

const SuggestContext = React.createContext();

export const useSuggest = () => {
  const context = React.useContext(SuggestContext);
  const {
    state, dispatch,
  } = context;

  const selectSecurityType = (value) =>
    dispatch({
      type: 'SEL_SECTYPE',
      securityType: value,
    });
  const inputSecurity = (security) => {
    if (state.requestController) {
      // If request is running when user inputs new value
      // we cancel running request
      state.requestController.abort();
      dispatch({
        type: 'REQ_CLEAR',
      });
    }
    dispatch({
      type: 'INPUT_SEC',
      input: security,
    });
  };
  const clearOptions = () =>
    dispatch({
      type: 'CLEAR_OPTS',
    });
  const clearInput = () =>
    dispatch({
      type: 'CLEAR_INPUT',
    });
  const searchSecurity = ({
    value, reason,
  }) => {
    const {
      securityType,
    } = state;

    const controller = new AbortController();

    dispatch({
      type: 'REQ_START',
      controller,
    });

    // eslint-disable-next-line
    const searchString = `/api/pricecoveragesuggest?security_type=${securityType}&s=${value}`;
    axios.get(process.env.API_URL + searchString, {
      signal: controller.signal,
    }).then((res) => res.data)
        .then((res) => dispatch({
          type: 'SEARCH_SEC',
          options: res.coverage,
          inputString: value,
        }));
  };

  return {
    state,
    selectSecurityType,
    inputSecurity,
    clearInput,
    clearOptions,
    searchSecurity,
  };
};

export const SuggestProvider = (props) => {
  const [
    state,
    dispatch,
  ] = React.useReducer(reducer, initialState);
  return <SuggestContext.Provider
    value={
      {
        state,
        dispatch,
      }
    }
    { ...props } />;
};
