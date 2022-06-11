import React from 'react';
import styled from 'styled-components';
import PropTypes from 'prop-types';
import {
  Link,
} from 'react-router-dom';

import {
  MenuIcon,
} from './components/menuicon';

const HeaderWrapper = styled.header`
  width: 100%;
  height: 10vh;

  a {
     text-decoration: none;
    color: inherit;
  }

`;

export const Header = ({
  showMenu, toggleMenu,
}) => {
  const PageHeaderInnerStyle = {
    maxWidth: '900px',
    margin: '0 auto',
    display: 'flex',
    justifyContent: 'space-between',
    width: '100%',
    height: '100%',
    alignItems: 'center',
  };

  const PageHeaderTitleStyle = {
    fontSize: '1.5rem',
    display: 'flex',
    alignItems: 'center',
    height: '100%',
  };

  const PageHeaderItemsStyle = {
    textAlign: 'right',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'flex-end',
    height: '100%',
  };

  return (
    <HeaderWrapper>
      <div
        style={ PageHeaderInnerStyle }>
        <div
          style={ PageHeaderTitleStyle }>
          <Link
            to='/'>
            <span>
              Pytho
            </span>
          </Link>
        </div>
        <div
          style={ PageHeaderItemsStyle }>
          <MenuIcon
            showMenu={ showMenu }
            toggleMenu={ toggleMenu } />
        </div>
      </div>
    </HeaderWrapper>
  );
};

Header.propTypes = {
  showMenu: PropTypes.bool.isRequired,
  toggleMenu: PropTypes.func.isRequired,
};

