import React from 'react';
import styled from 'styled-components';
import {
  Link,
} from 'react-router-dom';

import {
  DoubleHorizontalSpacer,
  ComponentWrapper,
  SectionWrapper,
  Text,
} from '@Style';

const HomeLinkWrapperStyle = styled.div`
  border: 1px solid var(--alt-background-color);
  padding: 0.5rem 0.5rem;
  cursor: pointer;
`;

const ComponentWrapperAddedVertical = styled(ComponentWrapper)`
  margin: 1rem 0.5rem;
  a {
    text-decoration: none;
    color: inherit;
  }
  div:hover:first-child,
  div:active:first-child {
    background-color: var(--alt-background-color);
  }
`;

const PageOpener = styled.div`
  display: flex;
  flex-direction: horizontal;
  justify-content: space-between;
  align-items: center;
`;

export const Home = (props) => {
  const HomeContentWrapperStyle = {
    maxWidth: '900px',
    margin: '0 auto',
    zIndex: '99',
    position: 'relative',
  };

  return (
    <SectionWrapper
      style={ HomeContentWrapperStyle }>
      <ComponentWrapperAddedVertical>
        <Text
          light
          focus>
          Creating tools for financial decisions
        </Text>
      </ComponentWrapperAddedVertical>
      <ComponentWrapperAddedVertical>
        <HomeLinkWrapperStyle>
          <Link
            to='/backtest'>
            <PageOpener>
              <Text
                focus>
                Portfolio Backtest
              </Text>
              <Text
                italic
                light>
                Click to open
              </Text>
            </PageOpener>
          </Link>
        </HomeLinkWrapperStyle>
        <DoubleHorizontalSpacer>
          <Text>
            Construct a portfolio and see how it perfomed historically.
          </Text>
        </DoubleHorizontalSpacer>
      </ComponentWrapperAddedVertical>
      <ComponentWrapperAddedVertical>
        <Link
          to='/exposureanalysis'>
          <HomeLinkWrapperStyle>
            <PageOpener>
              <Text
                focus>
                Exposure Analysis
              </Text>
              <Text
                italic
                light>
                Click to open
              </Text>
            </PageOpener>
          </HomeLinkWrapperStyle>
        </Link>
        <DoubleHorizontalSpacer>
          <Text>
            Quantifies exposure of an asset to another asset.
          </Text>
          <Text>
            Such as:
            <ul
              style={
                {
                  margin: '0',
                }
              }>
              <li>
                What % of fund X`&apos;`s returns are due to market exposure?
              </li>
              <li>
                What exposure does fund X have to asset class Y?
              </li>
            </ul>
          </Text>
          <Text>
          </Text>
        </DoubleHorizontalSpacer>
      </ComponentWrapperAddedVertical>
    </SectionWrapper>
  );
};

