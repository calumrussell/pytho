import React from 'react';
import axios from 'axios';

import {
  useMessage,
} from '@Components/reducers/message';

const isEmptyObj = (obj) => Object.keys(obj).length === 0;

const initialState = {
  independent: {},
  dependent: undefined,
  results: {},
  security: null,
  isRunnable: false,
  hasIndependent: false,
  hasDependent: false,
};

const actionTypes = {
  addDep: 'ADD_DEP',
  addInd: 'ADD_IND',
  removeDep: 'DEL_DEP',
  removeInd: 'DEL_IND',
  addResults: 'RES',
  addSecurity: 'ADD_SEC',
  clearResults: 'CLR_RES',
};

const reducer = (state, action) => {
  switch (action.type) {
    case actionTypes.addDep: {
      let isRunnable = true;
      if (isEmptyObj(state.independent)) {
        isRunnable = false;
      }

      return {
        ...state,
        dependent: state.security,
        security: null,
        isRunnable,
        hasDependent: true,
      };
    }

    case actionTypes.addInd: {
      const currentInd = state.independent;
      let isRunnable = true;
      if (!state.dependent) {
        isRunnable = false;
      }

      return {
        ...state,
        independent: {
          [state.security.id]: state.security,
          ...currentInd,
        },
        security: null,
        isRunnable,
        hasIndependent: true,
      };
    }

    case actionTypes.removeDep: {
      return {
        ...state,
        dependent: undefined,
        isRunnable: false,
        hasDependent: false,
      };
    }

    case actionTypes.removeInd: {
      const currentIndState = state.independent;
      delete currentIndState[action.id];

      let isRunnable = true;
      let hasIndependent = true;
      if (isEmptyObj(currentIndState)) {
        isRunnable = false;
        hasIndependent = false;
      } else if (!state.dependent) {
        isRunnable = false;
      }

      return {
        ...state,
        independent: currentIndState,
        hasIndependent,
        isRunnable,
      };
    }

    case actionTypes.clearResults: {
      return {
        ...state,
        results: {},
      };
    }

    case actionTypes.addResults: {
      return {
        ...state,
        results: action.results,
      };
    }

    case actionTypes.addSecurity: {
      return {
        ...state,
        security: action.security,
      };
    }

    default:
      new Error('Unknown action type');
  }
};

const ModelContext = React.createContext();

export const useModel = () => {
  const context = React.useContext(ModelContext);
  const {
    state, dispatch,
  } = context;

  const {
    errorMessage,
  } = useMessage();

  const addDependent = () => dispatch({
    type: 'ADD_DEP',
  });
  const addIndependent = () => dispatch({
    type: 'ADD_IND',
  });
  const removeIndependent = (id) => dispatch({
    type: 'DEL_IND',
    id,
  });
  const removeDependent = () => dispatch({
    type: 'DEL_DEP',
  });
  const addSecurity = (security) => dispatch({
    type: 'ADD_SEC',
    security,
  });

  const parseError = (error) => {
    if (error.response) {
      errorMessage(error.response.data.message);
    } else if (error.request) {
      errorMessage('No response');
    } else {
      errorMessage(error.message);
    }
  };

  const runCore = (finallyFunc) => {
    const {
      independent, dependent, results,
    } = state;

    if (results) {
      dispatch({
        type: 'CLR_RES',
      });
    }

    const indString = Object.keys(independent).map((v) => `ind=${v}`);
    const riskAttrQs = indString.join('&') + `&dep=${dependent.id}`;

    axios.get(process.env.API_URL + `/api/riskattribution?${riskAttrQs}`)
        .then((res) => res.data)
        .then((res) => dispatch({
          type: 'RES',
          results: {
            core: res.core,
            bootstrap: res.bootstrap,
            rolling: res.rolling,
          },
        }))
        .catch((error) => parseError(error))
        .finally(finallyFunc);
  };

  const runDrawdownEstimator = (finallyFunc) => {
    const {
      independent, dependent, results,
    } = state;

    if (results) {
      dispatch({
        type: 'CLR_RES',
      });
    }

    const indString = Object.keys(independent).map((v) => `ind=${v}`);
    const riskAttrQs = indString.join('&') + `&dep=${dependent.id}`;

    axios.get(process.env.API_URL + `/api/hypotheticaldrawdown?${riskAttrQs}`)
        .then((res) => res.data)
        .then((res) => dispatch({
          type: 'RES',
          results: {
            drawdown: res,
          },
        }))
        .catch((error) => parseError(error))
        .finally(finallyFunc);
  };

  return {
    state,
    addDependent,
    addIndependent,
    removeIndependent,
    removeDependent,
    runCore,
    runDrawdownEstimator,
    addSecurity,
  };
};

export const ModelProvider = (props) => {
  const [
    state,
    dispatch,
  ] = React.useReducer(reducer, initialState);
  return <ModelContext.Provider
    value={
      {
        state,
        dispatch,
      }
    }
    { ...props } />;
};
