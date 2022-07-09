import React from 'react';

import {
  BacktestProvider,
} from '@Components/reducers/backtest';
import {
  LoaderProvider,
} from '@Components/reducers/loader';
import {
  PortfolioBuilder,
  PortfolioDisplay,
  PortfolioProvider,
  PortfolioLoader,
} from '@Components/portfolio';
import {
  SectionWrapper, ComponentWrapper,
} from '@Style';

import {
  Results,
} from './results';

const Aphrodite = (props) => {
  return (
    <>
      <SectionWrapper
        data-testid="app">
        <ComponentWrapper>
          <PortfolioBuilder />
          <PortfolioDisplay />
          <PortfolioLoader />
        </ComponentWrapper>
      </SectionWrapper>
      <SectionWrapper>
        <Results />
      </SectionWrapper>
    </>
  );
};

export const AphroditeApp = (props) => {
  return (
    <PortfolioProvider>
      <BacktestProvider>
        <LoaderProvider>
          <Aphrodite
            { ...props } />
        </LoaderProvider>
      </BacktestProvider>
    </PortfolioProvider>
  );
};
