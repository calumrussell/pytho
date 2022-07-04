import React from "react"

import { ComponentWrapper, SectionWrapper, Title, Text } from '@Style';
import { useAntevorta } from '../../reducers/antevorta';

export const ModelResults = props => {

  const {
    state
  } = useAntevorta();

  if (state.results) {
    const  {
      cash,
      isa,
      gia,
      sipp
    } = state.results;
    return (
      <SectionWrapper>
        <ComponentWrapper>
          <Title>Cash</Title>
          <Text>{cash}</Text>
          <Title>ISA</Title>
          <Text>{isa}</Text>
          <Title>GIA</Title>
          <Text>{gia}</Text>
          <Title>SIPP</Title>
          <Text>{sipp}</Text>
        </ComponentWrapper>
      </SectionWrapper>
    )
  } else {
    return null;
  }
}
