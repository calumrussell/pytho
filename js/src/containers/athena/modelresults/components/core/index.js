import React from 'react';
import PropTypes from 'prop-types';

import {
  Title,
  Text,
  NumberWithTitle,
} from '@Components/common';
import {
  strConverterMult,
  strConverter,
  annualiseMonthlyRet,
} from '@Helpers';
import {
  ComponentWrapper,
  DefaultHorizontalSpacer,
  PanelWrapper,
} from '@Style';

const regressionCoefficient = PropTypes.shape({
  asset: PropTypes.number.isRequired,
  coef: PropTypes.number.isRequired,
  error: PropTypes.number.isRequired,
}).isRequired;

const regressionCoefficients = PropTypes.arrayOf(
    regressionCoefficient).isRequired;

const regressionResult = PropTypes.shape({
  intercept: PropTypes.number.isRequired,
  coefficients: regressionCoefficients,
}).isRequired;

const avg = PropTypes.shape({
  asset: PropTypes.number.isRequired,
  avg: PropTypes.number.isRequired,
}).isRequired;
const avgsResult = PropTypes.arrayOf(avg).isRequired;

const coreResult = PropTypes.shape({
  regression: regressionResult,
  avgs: avgsResult,
  min_date: PropTypes.number.isRequired,
  max_date: PropTypes.number.isRequired,
}).isRequired;

const rollingResult = PropTypes.shape({
  regressions: PropTypes.arrayOf(regressionResult).isRequired,
  averages: PropTypes.arrayOf(avgsResult),
  min_date: PropTypes.number.isRequired,
  max_date: PropTypes.number.isRequired,
  dates: PropTypes.arrayOf(PropTypes.number.isRequired).isRequired,
}).isRequired;

const bootstrapResult = PropTypes.shape({
  intercept: PropTypes.shape({
    asset: PropTypes.number.isRequired,
    lower: PropTypes.number.isRequired,
    upper: PropTypes.number.isRequired,
  }).isRequired,
  coefficients: PropTypes.arrayOf(
      PropTypes.shape({
        asset: PropTypes.number.isRequired,
        lower: PropTypes.number.isRequired,
        upper: PropTypes.number.isRequired,
      }).isRequired,
  ).isRequired,
}).isRequired;

const results = PropTypes.shape({
  'bootstrap': bootstrapResult,
  'rolling': rollingResult,
  'core': coreResult,
}).isRequired;

const Independent = ({
  results: {
    core, bootstrap,
  }, independent,
}) => {
  const annualisedRet = annualiseMonthlyRet(
      core.avgs.find((avg) => avg.asset == independent.id).avg);
  const coef = core.regression.coefficients.find(
      (coef) => coef.asset == independent.id).coef;

  const bootstrapEst = bootstrap.coefficients.find(
      (coef) => coef.asset == independent.id,
  );
  const lower = bootstrapEst.lower;
  const upper = bootstrapEst.upper;
  return (
    <PanelWrapper>
      <Text
        light>
        {independent.name}
      </Text>
      <DefaultHorizontalSpacer
        style={
          {
            display: 'flex',
          }
        }>
        <NumberWithTitle
          title={ 'Coef 5%' }
          number={ strConverter(lower) } />
        <NumberWithTitle
          title={ 'Coef' }
          number={ strConverter(coef) } />
        <NumberWithTitle
          title={ 'Coef 95%' }
          number={ strConverter(upper) } />
        <NumberWithTitle
          hasPercentage
          title={ 'Avg Ret' }
          number={ strConverterMult(annualisedRet) } />
        <NumberWithTitle
          hasPercentage
          title={ 'Attr 5%' }
          number={ strConverterMult(lower*annualisedRet) } />
        <NumberWithTitle
          hasPercentage
          title={ 'Attr 95%' }
          number={ strConverterMult(upper*annualisedRet) } />
      </DefaultHorizontalSpacer>
    </PanelWrapper>
  );
};

Independent.propTypes = {
  results: results,
  independent: PropTypes.shape({
    id: PropTypes.number.isRequired,
    name: PropTypes.string.isRequired,
  }),
};

const Independents = ({
  results, independent,
}) => {
  const assetIds = Object.keys(independent);
  return (
    <>
      <div
        style={
          {
            margin: '0.5rem 0 0 0',
          }
        }>
        {
          assetIds.map((assetId) => <Independent
            key={ assetId }
            results={ results }
            independent={ independent[assetId] } />)
        }
      </div>
    </>
  );
};

Independents.propTypes = {
  results: results,
  independent: PropTypes.arrayOf(
      PropTypes.shape({
        id: PropTypes.number.isRequired,
        name: PropTypes.string.isRequired,
      }).isRequired,
  ).isRequired,
};

const Dependent = ({
  results: {
    core, bootstrap,
  }, dependent,
}) => {
  const annualisedAvgRet = annualiseMonthlyRet(
      core.avgs.find((v) => v.asset == dependent.id).avg);
  const annualisedAlpha = annualiseMonthlyRet(core.regression.intercept);
  const lower = annualiseMonthlyRet(bootstrap.intercept.lower);
  const upper = annualiseMonthlyRet(bootstrap.intercept.upper);
  return (
    <PanelWrapper>
      <Text
        light>
        {dependent.name}
      </Text>
      <DefaultHorizontalSpacer
        style={
          {
            display: 'flex',
          }
        }>
        <NumberWithTitle
          hasPercentage
          title={ 'Alpha 5%' }
          number={ strConverterMult(lower) } />
        <NumberWithTitle
          hasPercentage
          title={ 'Alpha' }
          number={ strConverterMult(annualisedAlpha) } />
        <NumberWithTitle
          hasPercentage
          title={ 'Alpha 95%' }
          number={ strConverterMult(upper) } />
        <NumberWithTitle
          hasPercentage
          title={ 'Avg Ret' }
          number={ strConverterMult(annualisedAvgRet) } />
      </DefaultHorizontalSpacer>
    </PanelWrapper>
  );
};

Dependent.propTypes = {
  results: results,
  dependent: PropTypes.shape({
    id: PropTypes.number.isRequired,
    name: PropTypes.string.isRequired,
  }).isRequired,
};

export const CoreResultComponent = (props) => {
  return (
    <ComponentWrapper>
      <Title>
        Coefficients with confidence intervals
      </Title>
      <Dependent
        { ...props } />
      <Independents
        { ...props } />
    </ComponentWrapper>
  );
};
