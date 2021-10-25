import React from 'react';

import {
  Button,
} from '@Components/common';
import {
  useBacktest,
} from '@Components/reducers/backtest';
import {
  usePortfolio,
} from '@Components/portfolio';
import {
  useLoader,
} from '@Components/reducers/loader';

export const Results = (props) => {
  const {
    state: btState,
    runBacktest,
    renderResults,
  } = useBacktest();

  const {
    state: loadingState,
    toggleLoader,
    renderLoader,
  } = useLoader();

  const {
    state: portfolioState,
  } = usePortfolio();

  const clickLogic = () => {
    const loader = toggleLoader();
    runBacktest(portfolioState.portfolio, loader);
  };

  const Loader = renderLoader();
  return (
    <div>
      <Button
        disabled={ loadingState.isLoading }
        onClick={ clickLogic }>
        Run Backtest
      </Button>
      {!btState.results || renderResults()}
      <div>
        <Loader />
      </div>
    </div>
  );
};
