import React from 'react';

import {
  usePortfolio,
} from '@Components/portfolio';
import {
  CancelIcon,
  Text,
} from '@Common';
import {
  DefaultHorizontalSpacer,
  PanelWrapper,
} from '@Style';

const rowStyle = {
  display: 'flex',
  alignItems: 'center',
};

const iconStyle = {
  paddingRight: '0.25rem',
};

export const PortfolioDisplay = (props) => {
  const {
    state,
    removeFromPortfolio,
    hasPortfolio,
  } = usePortfolio();

  const {
    portfolio,
  } = state;

  if (hasPortfolio()) {
    // Ascending array 1..number of positions in portfolio
    const positions = Array(portfolio.getLength()).fill().map((v, i) => i);
    const p = portfolio.getPortfolio();

    return (
      <PanelWrapper>
        {
          positions.map((i) => {
            return (
              <DefaultHorizontalSpacer
                style={ rowStyle }
                key={ p.assets[i].id }>
                <CancelIcon
                  style={ iconStyle }
                  data-testid="backtest-removeassetbutton"
                  onClick={ () => removeFromPortfolio(i) } />
                <Text>
                  {p.assets[i].name}
                  {' '}
                  -
                  {' '}
                  {p.weights[i]}
                </Text>
              </DefaultHorizontalSpacer>
            );
          })
        }
      </PanelWrapper>
    );
  }
  return null;
};
