import React, {
  useEffect,
} from 'react';
import Autosuggest from 'react-autosuggest';
import PropTypes from 'prop-types';

import {
  FormSelect,
  FormLabel,
} from '@Components/form';

import {
  useSuggest,
  SuggestProvider,
} from './reducers/suggest';

const willRenderFunc = (val) => {
  return (
    val.name ?
    val.name.trim().length > 2 :
    val.trim().length > 2
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
    selectSecurityType,
    searchSecurity,
    inputSecurity,
  } = useSuggest();

  const {
    securitiesOptions,
    securitySearch,
    securityType,
    securityTypes,
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
    <>
      <FormLabel
        htmlFor="portfoliosearch-securitytype">
        Security Type
      </FormLabel>
      <FormSelect
        id="portfoliosearch-securitytype"
        data-testid="portfoliosearch-securitytype-dropdown"
        value={ securityType }
        options={ securityTypes }
        onChange={ (e) => selectSecurityType(e.target.value) } />
      <FormLabel
        htmlFor="portfoliosearch-asset">
        Asset
      </FormLabel>
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
        getSuggestionValue={ (item) => item.name }
        renderSuggestion={
          (item) => (
            <span>
              {item.name}
            </span>
          )
        }
        inputProps={
          {
            id: 'portfoliosearch-asset',
            placeholder: 'Search Security',
            value: securitySearch,
            onChange: (e, {
              newValue,
            } )=>{
              inputSecurity(newValue);
            },
          }
        }
      />
    </>
  );
};

PortfolioSearchInner.propTypes = {
  selectHook: PropTypes.func.isRequired,
  shouldClear: PropTypes.bool.isRequired,
  runAfterClear: PropTypes.func.isRequired,
};

export const PortfolioSearch = (props) => {
  return (
    <SuggestProvider>
      <PortfolioSearchInner
        { ...props } />
    </SuggestProvider>
  );
};

