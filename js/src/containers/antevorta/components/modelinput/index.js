import React, {
  useState,
} from 'react';

import {
  SectionWrapper,
  ComponentWrapper,
  Button,
} from '@Style';
import {
  PortfolioBuilder,
  PortfolioDisplay,
  PortfolioLoader,
  usePortfolio,
} from '@Components/portfolio';
import {
  FormWrapper,
  FormInput,
  FormLabel,
} from '@Components/form';
import {
  useLoader,
} from '@Components/reducers/loader';

import {
  useAntevorta,
} from '../../reducers/antevorta/';

export const ModelInput = (props) => {
  const [
    initialCash,
    setInitialCash,
  ] = useState(1000);
  const [
    wage,
    setWage,
  ] = useState(1000);
  const [
    wageGrowth,
    setWageGrowth,
  ] = useState(1);
  const [
    emergencyCashMin,
    setEmergencyCashMin,
  ] = useState(5000);
  const [
    contributionPct,
    setContributionPct,
  ] = useState(5);
  const [
    simLength,
    setSimLength,
  ] = useState(10);

  const {
    runSim,
    simInputBuilder,
    clearSim,
  } = useAntevorta();

  const {
    toggleLoader,
  } = useLoader();

  const {
    state: portfolioState,
  } = usePortfolio();

  const runSimWrapper = () => {
    const loader = toggleLoader();
    const simInput = simInputBuilder(
        portfolioState, initialCash, wage, wageGrowth, contributionPct, emergencyCashMin, simLength);
    runSim(simInput, loader);
  };

  const clickWrapper = (ev, func) => {
    ev.preventDefault();
    func(ev.target.value);
  };

  return (
    <SectionWrapper>
      <ComponentWrapper>
        <PortfolioBuilder />
        <PortfolioDisplay />
        <PortfolioLoader />
      </ComponentWrapper>
      <FormWrapper>
        <FormLabel
          htmlFor="antevorta-initialcash-input">
          Initial Cash
        </FormLabel>
        <FormInput
          id="antevorta-initialcash-input"
          type="number"
          value={ initialCash }
          min="1000"
          step="1000"
          onChange={ (ev) => clickWrapper(ev, setInitialCash) } />
        <FormLabel
          htmlFor="antevorta-wage-input">
          Wage
        </FormLabel>
        <FormInput
          id="antevorta-wage-input"
          type="number"
          value={ wage }
          min="1000"
          step="1000"
          onChange={ (ev) => clickWrapper(ev, setWage) } />
        <FormLabel
          htmlFor="antevorta-wagegrowth-input">
          Wage Growth %
        </FormLabel>
        <FormInput
          id="antevorta-wagegrowth-input"
          type="number"
          min="0"
          max="40"
          value={ wageGrowth }
          onChange={ (ev) => clickWrapper(ev, setWageGrowth) } />
        <FormLabel
          htmlFor="antevorta-contributionpct-input">
          Contribution Percentage (%)
        </FormLabel>
        <FormInput
          id="antevorta-contributionpct-input"
          type="number"
          min="1"
          max="100"
          value={ contributionPct }
          onChange={ (ev) => clickWrapper(ev, setContributionPct) } />
        <FormLabel
          htmlFor="antevorta-contributionpct-input">
          Emergency Cash Minimum
        </FormLabel>
        <FormInput
          id="antevorta-emergencycashmin-input"
          type="number"
          min="1000"
          step="1000"
          value={emergencyCashMin}
          onChange={ (ev) => clickWrapper(ev, setEmergencyCashMin) } />
        <FormLabel
          htmlFor="antevorta-simlength-input">
          Simulation Length (yrs)
        </FormLabel>
         <FormInput
          id="antevorta-simlength-input"
          type="number"
          min="10"
          max="30"
          value={simLength}
          onChange={ (ev) => clickWrapper(ev, setSimLength) } />
      </FormWrapper>
      <Button
        onClick={ () => runSimWrapper() }>
        Run
      </Button>
      <Button
        onClick={ () => clearSim() }>
        Clear
      </Button>
    </SectionWrapper>
  );
};
