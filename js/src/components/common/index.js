import React from 'react';
import PropTypes from 'prop-types';

import {
  useMessage,
} from '@Components/reducers/message';

import {
  MessageSuccess,
  MessageError,
  Button as ButtonStyle,
  Text,
  Title as TitleStyle,
} from './style.js';

export const PlusIcon = (props) => (
  <svg
    { ...props }
    height="1.25rem"
    width="1.25rem"
    aria-hidden="true"
    focusable="false"
    data-prefix="fas"
    data-icon="plus"
    className="plus-icon"
    role="img"
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 448 512">
    <path
      shapeRendering="crispEdges"
      fill="currentColor"
      // eslint-disable-next-line
      d="M416 208H272V64c0-17.67-14.33-32-32-32h-32c-17.67 0-32 14.33-32 32v144H32c-17.67 0-32 14.33-32 32v32c0 17.67 14.33 32 32 32h144v144c0 17.67 14.33 32 32 32h32c17.67 0 32-14.33 32-32V304h144c17.67 0 32-14.33 32-32v-32c0-17.67-14.33-32-32-32z">
    </path>
  </svg>
);

export const MinusIcon = (props) => (
  <svg
    { ...props }
    height="1.25rem"
    width="1.25rem"
    aria-hidden="true"
    focusable="false"
    data-prefix="fas"
    data-icon="minus"
    className="minus-icon"
    role="img"
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 448 512">
    <path
      shapeRendering="crispEdges"
      fill="currentColor"
      // eslint-disable-next-line
      d="M416 208H32c-17.67 0-32 14.33-32 32v32c0 17.67 14.33 32 32 32h384c17.67 0 32-14.33 32-32v-32c0-17.67-14.33-32-32-32z">
    </path>
  </svg>
);

export const BarChartIcon = (props) => (
  <svg
    { ...props }
    height="1.25rem"
    width="1.25rem"
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    stroke="currentColor">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="2"
      // eslint-disable-next-line
      d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
  </svg>
);

export const CancelIcon = (props) => (
  <svg
    { ...props }
    height="1.25rem"
    width="1.25rem"
    aria-hidden="true"
    focusable="false"
    data-prefix="fas"
    data-icon="times-circle"
    className="svg-inline--fa fa-times-circle fa-w-16"
    role="img"
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 512 512">
    <path
      fill="currentColor"
      // eslint-disable-next-line
      d="M256 8C119 8 8 119 8 256s111 248 248 248 248-111 248-248S393 8 256 8zm121.6 313.1c4.7 4.7 4.7 12.3 0 17L338 377.6c-4.7 4.7-12.3 4.7-17 0L256 312l-65.1 65.6c-4.7 4.7-12.3 4.7-17 0L134.4 338c-4.7-4.7-4.7-12.3 0-17l65.6-65-65.6-65.1c-4.7-4.7-4.7-12.3 0-17l39.6-39.6c4.7-4.7 12.3-4.7 17 0l65 65.7 65.1-65.6c4.7-4.7 12.3-4.7 17 0l39.6 39.6c4.7 4.7 4.7 12.3 0 17L312 256l65.6 65.1z">
    </path>
  </svg>
);

export const Message = (props) => {
  const {
    state,
  } = useMessage();
  const {
    message,
    messageType,
  } = state;

  if (!message) return null;
  if (messageType == 'SUCCESS') {
    return (
      <MessageSuccess
        { ...props }>
        {message}
      </MessageSuccess>
    );
  } else if (messageType == 'ERROR') {
    return (
      <MessageError
        { ...props }>
        {message}
      </MessageError>
    );
  } else {
    return null;
  }
};

export const Button = (props) => (
  <ButtonStyle
    { ...props }>
    {props.children}
  </ButtonStyle>
);

Button.propTypes = {
  children: PropTypes.node.isRequired,
  disabled: PropTypes.bool,
};

export const RenderIf = ({
  cond, children,
}) => {
  return (
    cond ? (
      <>
        {children}
      </>
    ) :
    null
  );
};

RenderIf.propTypes = {
  cond: PropTypes.bool.isRequired,
  children: PropTypes.node.isRequired,
};

export const Title = (props) => {
  return (
    <TitleStyle
      { ...props }>
      {props.children}
    </TitleStyle>
  );
};

Title.propTypes = {
  light: PropTypes.bool,
  children: PropTypes.node.isRequired,
};

export {
  Text,
};

/*
export const Text = (props) => {
  return (
    <TextStyle
      { ...props }>
      {props.children}
    </TextStyle>
  );
};

Text.propTypes = {
  highlight: PropTypes.bool,
  children: PropTypes.node.isRequired,
};
*/

export const NumberWithTitle = ({
  title, number, hasPercentage,
}) => {
  const cellStyle = {
    display: 'flex',
    alignItems: 'flex-end',
    justifyContent: 'flex-end',
  };

  return (
    <div
      style={
        {
          margin: '0.25rem 0.5rem 0 0',
          width: '100px',
        }
      }>
      <Title
        style={ cellStyle }
        light>
        {title}
      </Title>
      <span
        style={ cellStyle }>
        <Text
          number
          highlight>
          {number}
        </Text>
        {
          !hasPercentage || (
            <Text
              light
              margin={ '0' }>
              %
            </Text>
          )
        }
      </span>
    </div>
  );
};

NumberWithTitle.propTypes = {
  title: PropTypes.string.isRequired,
  number: PropTypes.string.isRequired,
  hasPercentage: PropTypes.bool,
};
