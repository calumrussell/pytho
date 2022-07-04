import React from 'react';

import {
  LoaderProvider,
} from '@Components/reducers/loader';
import {
  PageWrapper,
} from '@Style';
import {
  PortfolioProvider
} from '@Components/portfolio';

import {
  AntevortaProvider,
} from './reducers/antevorta/';
import {
  ModelInput,
} from './components/modelinput/';
import {
  ModelResults,
} from './components/modelresults';


export const AntevortaApp = (props) => (
  <PageWrapper id="antevorta-main">
    <AntevortaProvider>
      <PortfolioProvider>
        <LoaderProvider>
          <ModelInput />
          <ModelResults />
        </LoaderProvider>
      </PortfolioProvider>
    </AntevortaProvider>
  </PageWrapper>
)
