import React from 'react';

import {
  ModelProvider,
} from '@Components/reducers/riskattribution';
import {
  LoaderProvider,
} from '@Components/reducers/loader';
import {
  PageWrapper,
} from '@Style';

import {
  ModelResults,
} from './modelresults';
import {
  Builder,
} from './builder';

const Athena = (props) => (
  <PageWrapper
    id="riskattribution-main">
    <Builder />
    <ModelResults />
  </PageWrapper>
);


export const AthenaApp = (props) => (
  <ModelProvider>
    <LoaderProvider>
      <Athena
        { ...props } />
    </LoaderProvider>
  </ModelProvider>
);
