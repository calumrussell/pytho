import React, {
  useState,
} from 'react';

import {
  Button,
} from '@Components/common';
import {
  FormWrapper,
} from '@Components/form';
import {
  useModel,
} from '@Components/reducers/riskattribution';
import {
  PortfolioSearch,
} from '@Components/portfolio';
import {
  SectionWrapper,
  ComponentWrapper,
} from '@Style';

import {
  ModelDefinition,
} from './components/modeldefinition';

export const Builder = (props) => {
  const {
    addSecurity,
    addDependent,
    addIndependent,
    state,
  } = useModel();

  const [
    shouldClear,
    setShouldClear,
  ] = useState(false);

  const clearHook = (func, e) => {
    e.preventDefault();
    func();
    setShouldClear(true);
  };

  return (
    <SectionWrapper>
      <ComponentWrapper>
        <FormWrapper>
          <PortfolioSearch
            runAfterClear={ () => setShouldClear(false) }
            shouldClear={ shouldClear }
            selectHook={ addSecurity } />
          <Button
            onClick={ (e) => clearHook(addIndependent, e) }>
            Add Independent
          </Button>
          <Button
            disabled={ state.hasDependent }
            onClick={ (e) => clearHook(addDependent, e) }>
            Add Dependent
          </Button>
        </FormWrapper>
      </ComponentWrapper>
      <ModelDefinition />
    </SectionWrapper>
  );
};
