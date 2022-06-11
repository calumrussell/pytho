import React from 'react';
import axios from 'axios';

const initialState = {
  securitySearch: '',
  securitiesOptions: [
  ],
  requestController: undefined,
};

const actionTypes = {
  clearInput: 'CLEAR_INPUT',
  clearOptions: 'CLEAR_OPTS',
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

const AlphaSuggestContext = React.createContext();

export const useAlphaSuggest = () => {
  const context = React.useContext(AlphaSuggestContext);
  const {
    state, dispatch,
  } = context;

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
    /* If the user has added more letters before the
    api responds, then we shouldn't update the search
    results.
    */

    // Only one request can run at a time, so we dispatch
    // a start event that can be cancelled if user inputs more
    const controller = new AbortController();
    dispatch({
      type: 'REQ_START',
      controller,
    });

    // eslint-disable-next-line
    const searchString = `/api/hermessuggest?&s=${value}`;
    axios.get(process.env.API_URL + searchString, {
      signal: controller.signal,
    }).then((res) => res.data)
        .then((res) => dispatch({
          type: 'SEARCH_SEC',
          options: res.results,
          inputString: value,
        }));
  };

  return {
    state,
    inputSecurity,
    clearInput,
    clearOptions,
    searchSecurity,
  };
};

export const AlphaSuggestProvider = (props) => {
  const [
    state,
    dispatch,
  ] = React.useReducer(reducer, initialState);
  return <AlphaSuggestContext.Provider
    value={
      {
        state,
        dispatch,
      }
    }
    { ...props } />;
};

