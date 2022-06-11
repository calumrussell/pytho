import React from 'react';
import PropTypes from 'prop-types';

import {
  LineChart,
} from '@Components/charts';
import {
  annualiseMonthlyRet,
} from '@Helpers';
import {
  ComponentWrapper,
  PanelWrapper,
} from '@Style';
import {
  Title,
} from '@Components/common';

const RollingCoefsLineChart = ({
  data, independent,
}) => {
  const assetIds = Object.keys(independent);
  const assetNames = Object.keys(independent).map((a) => independent[a].name);
  const yValues = assetIds.map(
      (assetId) => data.regressions.map(
          (d) => d.coefficients.find((coef) => coef.asset == assetId).coef));
  const dates = data.dates;

  const rootId = 'chart-container-exposure-coefs';
  return (
    <LineChart
      rootId={ rootId }
      labels={ assetNames }
      xValues={ dates }
      yValues={ yValues } />
  );
};

RollingCoefsLineChart.propTypes = {
  data: PropTypes.shape({
    regressions: PropTypes.arrayOf(PropTypes.shape({
      coefficients: PropTypes.arrayOf(PropTypes.shape({
        asset: PropTypes.number.isRequired,
        coef: PropTypes.number.isRequired,
      })),
    })),
    dates: PropTypes.arrayOf(PropTypes.number).isRequired,
  }),
  independent: PropTypes.object.isRequired,
};

const RollingAlphaLineChart = ({
  data,
}) => {
  const dates = data.dates;
  const yValues = [
    data.regressions.map((d) => annualiseMonthlyRet(d.intercept)),
  ];
  const rootId = 'chart-container-exposure-alpha';
  return (
    <LineChart
      rootId={ rootId }
      labels={
        [
          'Alpha',
        ]
      }
      xValues={ dates }
      yValues={ yValues } />
  );
};

RollingAlphaLineChart.propTypes = {
  data: PropTypes.shape({
    regressions: PropTypes.arrayOf(PropTypes.shape({
      intercept: PropTypes.number.isRequired,
    })),
    dates: PropTypes.arrayOf(PropTypes.number).isRequired,
  }),
};


export const RollingResultComponent = ({
  rolling, independent,
}) => {
  return (
    <ComponentWrapper>
      <Title>
        6-month rolling estimates
      </Title>
      <PanelWrapper>
        <RollingAlphaLineChart
          data={ rolling } />
        <RollingCoefsLineChart
          data={ rolling }
          independent={ independent } />
      </PanelWrapper>
    </ComponentWrapper>
  );
};

RollingResultComponent.propTypes = {
  rolling: PropTypes.object.isRequired,
  independent: PropTypes.object.isRequired,
};
