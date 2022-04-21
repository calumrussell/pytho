import React, {
  useState,
} from 'react';

import {
  FormWrapper,
  FormLabel,
  FormInput,
} from '@Components/form';
import {
  PortfolioSearch,
  usePortfolio,
} from '@Components/portfolio';
import {
  Button,
} from '@Common';

export const BuilderForm = (props) => {
  const [
    shouldClear,
    setShouldClear,
  ] = useState(false);

  const [
    weight,
    setWeight,
  ] = useState('');

  const [
    security,
    setSecurity,
  ] = useState('');

  const isFinished = security && weight != '';

  const {
    addToPortfolio,
  } = usePortfolio();

  const portfolioAdder = () => {
    addToPortfolio(security, weight);
    setShouldClear(true);
    setWeight('');
    setSecurity('');
  };

  return (
    <>
      <FormWrapper>
        <FormLabel>
          Weight (%)
        </FormLabel>
        <FormInput
          data-testid="backtest-weight-input"
          type="text"
          name="weight"
          placeholder="Input asset weight %"
          value={ weight }
          onChange={ (e) => setWeight(e.target.value) } />
        <FormLabel>
          Asset
        </FormLabel>
        <PortfolioSearch
          runAfterClear={ () => setShouldClear(false) }
          shouldClear={ shouldClear }
          selectHook={ (s) => setSecurity(s) } />
      </FormWrapper>
      <Button
        disabled={ !isFinished }
        onClick={ () => portfolioAdder() }>
        Add to portfolio
      </Button>
    </>
  );
};
