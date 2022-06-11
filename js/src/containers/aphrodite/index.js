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
  PageWrapper, SectionWrapper, ComponentWrapper,
} from '@Style';

import {
  Results,
} from './results';

const Aphrodite = (props) => {
  return (
    <PageWrapper
      data-testid="app">
      <SectionWrapper>
        <ComponentWrapper>
          <PortfolioBuilder />
          <PortfolioDisplay />
          <PortfolioLoader />
        </ComponentWrapper>
      </SectionWrapper>
      <Results />
    </PageWrapper>
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
