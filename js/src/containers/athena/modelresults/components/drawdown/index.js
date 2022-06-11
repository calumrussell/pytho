import React from 'react';
import PropTypes from 'prop-types';

import {
  Title,
  NumberWithTitle,
} from '@Components/common';
import {
  strConverterMult,
  strConverter,
  annualiseMonthlyRet,
} from '@Helpers';
import {
  ComponentWrapper,
} from '@Style';

const Independent = ({
  results, independent,
}) => {
  const coef = results.regressions.coefficients.find(
      (coef) => coef.asset == independent.id).coef;

  return (
    <>
      <Title>
        {independent.name}
      </Title>
      <div
        style={
          {
            display: 'flex',
          }
        }>
        <NumberWithTitle
          title={ 'Coef' }
          number={ strConverter(coef) } />
      </div>
    </>
  );
};

Independent.propTypes = {
  results: PropTypes.shape({
    regressions: PropTypes.shape({
      coefficients: PropTypes.arrayOf(
          PropTypes.shape({
            asset: PropTypes.number.isRequired,
            coef: PropTypes.number.isRequired,
          }),
      ),
    }),
  }),
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
  results: PropTypes.object.isRequired,
  independent: PropTypes.object.isRequired,
};

const Dependent = ({
  results, dependent,
}) => {
  const annualisedAlpha = annualiseMonthlyRet(results.regressions.intercept);

  return (
    <>
      <div
        style={
          {
            margin: '0.5rem 0 0 0',
          }
        }>
        <Title>
          {dependent.name}
        </Title>
        <div
          style={
            {
              display: 'flex',
            }
          }>
          <NumberWithTitle
            hasPercentage
            title={ 'Alpha' }
            number={ strConverterMult(annualisedAlpha) } />
        </div>
      </div>
    </>
  );
};

Dependent.propTypes = {
  results: PropTypes.shape({
    regressions: PropTypes.shape({
      intercept: PropTypes.number.isRequired,
    }),
  }),
  dependent: PropTypes.shape({
    name: PropTypes.string.isRequired,
  }),
};

export const Drawdown = ({
  start, end, mean,
}) => {
  return (
    <div
      style={
        {
          'display': 'flex',
        }
      }>
      <span>
        {start}
        {' '}
        -
        {' '}
        {end}
      </span>
      <span>
        {mean}
      </span>
    </div>
  );
};

Drawdown.propTypes = {
  start: PropTypes.string.isRequired,
  end: PropTypes.string.isRequired,
  mean: PropTypes.number.isRequired,
};

export const Drawdowns = ({
  results,
}) => {
  return (
    <div>
      {
        results.drawdowns.map((dd, i) => <Drawdown
          key={ i }
          { ...dd } />)
      }
    </div>
  );
};

Drawdowns.propTypes = {
  results: PropTypes.shape({
    drawdowns: PropTypes.arrayOf(PropTypes.object).isRequired,
  }),
};

export const DrawdownEstimatorResults = (props) => {
  return (
    <ComponentWrapper>
      <Independents
        { ...props } />
      <Dependent
        { ...props } />
      <Drawdowns
        { ...props } />
    </ComponentWrapper>
  );
};
