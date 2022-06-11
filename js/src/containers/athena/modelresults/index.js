import React from 'react';

import {
  useModel,
} from '@Components/reducers/riskattribution';
import {
  PanelWrapper,
  SectionWrapper,
} from '@Style';

import {
  CoreResultComponent,
} from './components/core';
import {
  DrawdownEstimatorResults,
} from './components/drawdown';
import {
  RollingResultComponent,
} from './components/rollingchart';

export const ModelResults = (props) => {
  const {
    state,
  } = useModel();
  const {
    results,
    independent,
    dependent,
  } = state;
  const {
    core, bootstrap, rolling, drawdown,
  } = results;

  if (core != undefined && bootstrap != undefined && rolling != undefined) {
    return (
      <SectionWrapper
        data-testid="riskattribution-modelresults">
        <PanelWrapper>
          <CoreResultComponent
            results={ results }
            independent={ independent }
            dependent={ dependent } />
          <RollingResultComponent
            rolling={ rolling }
            independent={ independent } />
        </PanelWrapper>
      </SectionWrapper>
    );
  } else if (drawdown != undefined) {
    return (
      <SectionWrapper
        data-testid="riskattribution-modelresults">
        <PanelWrapper>
          <DrawdownEstimatorResults
            results={ drawdown }
            independent={ independent }
            dependent={ dependent } />
        </PanelWrapper>
      </SectionWrapper>
    );
  }

  return null;
};
