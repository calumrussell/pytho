import React, {
  useEffect,
} from 'react';
import Autosuggest from 'react-autosuggest';
import PropTypes from 'prop-types';

import {
  useAlphaSuggest,
  AlphaSuggestProvider,
} from './reducers/suggest';

const willRenderFunc = (val) => {
  return (
    val.Name ?
    val.Name.trim().length > 1 :
    val.trim().length > 1
  );
};

export const PortfolioSearchInner = ({
  selectHook,
  shouldClear,
  runAfterClear,
}) => {
  const {
    state,
    clearOptions,
    clearInput,
    searchSecurity,
    inputSecurity,
  } = useAlphaSuggest();

  const {
    securitiesOptions,
    securitySearch,
  } = state;

  const selectFunc = (suggestion) => {
    selectHook(suggestion);
  };

  useEffect((() => {
    if (shouldClear) {
      clearInput();
      runAfterClear();
    }
  }), [
    shouldClear,
  ]);

  return (
    <div>
      <Autosuggest
        suggestions={ securitiesOptions }
        shouldRenderSuggestions={ (v) => willRenderFunc(v) }
        onSuggestionsClearRequested={ () => clearOptions() }
        onSuggestionSelected={
          (e, {
            suggestion,
          }) => selectFunc(suggestion)
        }
        onSuggestionsFetchRequested={ searchSecurity }
        getSuggestionValue={ (item) => item.Name }
        renderSuggestion={
          (item) => (
            <span>
              {item.Name}
              {' '}
              -
              {item.Country}
            </span>
          )
        }
        inputProps={
          {
            placeholder: 'Search Company',
            value: securitySearch,
            onChange: (e, {
              newValue,
            } )=>{
              inputSecurity(newValue);
            },
          }
        }
      />
    </div>
  );
};

PortfolioSearchInner.propTypes = {
  selectHook: PropTypes.func.isRequired,
  shouldClear: PropTypes.bool.isRequired,
  runAfterClear: PropTypes.func.isRequired,
};

export const AlphaSearch = (props) => {
  return (
    <AlphaSuggestProvider>
      <PortfolioSearchInner
        { ...props } />
    </AlphaSuggestProvider>
  );
};

