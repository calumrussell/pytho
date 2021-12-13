import React from 'react';
import PropTypes from 'prop-types';

import {
  LineChartWithBrush,
} from '@Components/charts';
import {
  NumberWithTitle,
} from '@Components/common';
import {
  strConverter,
} from '@Helpers';

export const PortfolioPerformance = ({
  results,
}) => {
  const {
    values,
    cagr,
    vol,
    mdd,
    dates,
  } = results;

  const wrapperStyle = {
    margin: '20px 0',
  };

  const numbersStyle = {
    display: 'flex',
    justifyContent: 'space-around',
  };

  return (
    <div
      style={ wrapperStyle }>
      <LineChartWithBrush
        labels={['Portfolio']}
        xValues={ dates }
        yValues={ [values]} />
      <div
        style={ numbersStyle }>
        <NumberWithTitle
          hasPercentage={ true }
          title={ 'Cagr' }
          number={ strConverter(cagr) } />
        <NumberWithTitle
          hasPercentage={ true }
          title={ 'Vol' }
          number={ strConverter(vol) } />
        <NumberWithTitle
          hasPercentage={ true }
          title={ 'MaxDD' }
          number={ strConverter(mdd) } />
      </div>
    </div>
  );
};

PortfolioPerformance.propTypes = {
  results: PropTypes.shape({
    values: PropTypes.array.isRequired,
    cagr: PropTypes.number.isRequired,
    vol: PropTypes.number.isRequired,
    mdd: PropTypes.number.isRequired,
    dates: PropTypes.array.isRequired,
  }),
};
