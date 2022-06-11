import styled from 'styled-components';

export const Title = styled.span`
  text-align: ${(props) => props.number ?
    'right' :
    props.align ?
    props.align :
    'justify'};
  font-size: 0.9rem;
  color: ${(props) => props.light ?
    'var(--alt-text-color)' :
    'var(--default-text-color)'};
`;

export const Text = styled.p`
  font-style: ${(props) => props.italic ?
      'italic':
      'normal'};
  text-align: ${(props) => props.align ?
      props.align :
      props.number ?
      'right':
      'justify'};
  font-size: ${(props) => props.highlight ?
     '1.4rem':
     props.focus ?
     '1.1rem' :
     props.small ?
     '0.75rem':
     '0.9rem'};
  line-height: ${(props) => props.highlight ? '1.15': '1.75'};
  color: ${(props) => props.light ?
    'var(--alt-text-color)' :
    'var(--default-text-color)'};
  margin: ${(props) => props.highlight ?
    '0.1rem 0' :
    props.margin ?
    props.margin :
    'initial'};
`;

// Page>Section>Component
// When we are down to the level of Component, the
// component itself is responsible for the positioning.

// This wraps the whole page under the header and footer
// Empty now but included if changes needed later
export const PageWrapper = styled.div``;

// This wraps a discrete section of the page that needs to be
// organized seperately from another section
// Not nested, designing for limited horizontal space so would
// lead to pyramid look if we nested and then added spacing later
// Empty now but included if changes needed later
export const SectionWrapper = styled.div`
  margin: 1rem 0;
`;

// This wraps elements within sections that need to be
// organized seperately from other components within
// that section.
export const ComponentWrapper = styled.div``;

export const DefaultHorizontalSpacer = styled.div`
  padding: 0rem 0.5rem;
`;

export const DoubleHorizontalSpacer = styled.div`
  padding: 0rem 1rem;
`;

// Generic wrapper that can be used to space objects within a
// component
export const PanelWrapper = styled(DefaultHorizontalSpacer)`
  margin: 0.5rem 0;
`;

export const BaseMessage = styled.div`
  box-sizing: border-box;
  margin 1rem 0;
  padding: 0.5rem;
  font-size: 1rem;
`;

export const MessageSuccess = styled(BaseMessage)`
  background: #4E937A;
  color: white;
`;

export const MessageError = styled(BaseMessage)`
  background: #B4656F;
  color: white;
`;

export const Button = styled.button`
  padding: ${(props) => props.icon ?
    '0.25rem 0.25rem' :
    '0.5rem 1rem'};
  margin: ${(props) => props.noMargin ?
    '0' :
    '0.5rem 0'};
  margin-right: 0.25rem;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 1rem;
  background: none;
  outline: ${(props) => props.success ?
    'none' :
    'initial'};
  color: ${(props) => props.disabled ?
    'var(--disabled-text-color)' :
    'var(--default-text-color)'};
  background-color: var(--alt-background-color);
  border: none;
  };
`;

export const PureButton = styled.button`

`;
