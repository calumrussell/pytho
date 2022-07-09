import React from 'react';
import styled from 'styled-components';

import {
  ComponentWrapper, SectionWrapper,
} from '@Style';
import {
  useAntevorta,
} from '../../reducers/antevorta';
import {
  NumberWithTitle,
} from '@Components/common';
import {
  strConverter,
} from '@Helpers';

const RowWrapper = styled.div`
  display: flex;
  justify-content: space-around;
  margin: 1rem 0;
`;

export const ModelResults = (props) => {
  const {
    state,
  } = useAntevorta();

  if (state.results) {
    const {
      cash,
      isa,
      gia,
      sipp,
    } = state.results;
    return (
      <SectionWrapper>
        <ComponentWrapper>
          <RowWrapper>
            <NumberWithTitle
              title={ 'Cash' }
              number={ strConverter(cash) } />
            <NumberWithTitle
              title={ 'ISA' }
              number={ strConverter(isa) } />
            <NumberWithTitle
              title={ 'GIA' }
              number={ strConverter(gia) } />
            <NumberWithTitle
              title={ 'SIPP' }
              number={ strConverter(sipp) } />
          </RowWrapper>
        </ComponentWrapper>
      </SectionWrapper>
    );
  } else {
    return null;
  }
};
