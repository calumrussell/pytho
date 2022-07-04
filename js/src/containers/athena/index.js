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

export const AthenaApp = (props) => (
  <ModelProvider id="riskattribution-main">
    <LoaderProvider>
      <Builder />
      <ModelResults />
    </LoaderProvider>
  </ModelProvider>
);
