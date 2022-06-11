import React, {
  useState,
} from 'react';
import PropTypes from 'prop-types';

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

export const BuilderForm = ({
  isEmpty,
  onClickSave,
}) => {
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
        <FormLabel
          htmlFor="aphrodite-weight">
          Weight (%)
        </FormLabel>
        <FormInput
          id="aphrodite-weight"
          data-testid="backtest-weight-input"
          type="text"
          name="weight"
          placeholder="Input asset weight %"
          value={ weight }
          onChange={ (e) => setWeight(e.target.value) } />
        <PortfolioSearch
          runAfterClear={ () => setShouldClear(false) }
          shouldClear={ shouldClear }
          selectHook={ (s) => setSecurity(s) } />
        <Button
          disabled={ !isFinished }
          onClick={ () => portfolioAdder() }>
          Add to portfolio
        </Button>
        <Button
          disabled={ isEmpty }
          onClick={ onClickSave }>
          Save portfolio
        </Button>
      </FormWrapper>
    </>
  );
};

BuilderForm.propTypes = {
  isEmpty: PropTypes.bool.isRequired,
  onClickSave: PropTypes.func.isRequired,
};
