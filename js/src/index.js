import React, {
  useState,
} from 'react';
import styled from 'styled-components';
import {
  BrowserRouter as Router,
  Switch,
  Route,
} from 'react-router-dom';

import {
  GlobalStyle,
} from './style.js';
import {
  AphroditeApp,
} from './containers/aphrodite';
import {
  AthenaApp,
} from './containers/athena';
import {
  AntevortaApp,
} from './containers/antevorta';
import {
  Home,
} from './components/home';
import {
  Header,
} from './components/header';
import {
  SideMenu,
} from './components/sidemenu';
import {
  UserProvider,
} from '@Components/reducers/user';
import {
  MessageProvider,
} from '@Components/reducers/message';
import {
  Message,
} from '@Common';

const AppWrapper = styled.div`
  font-family: "Open Sans";
  color: var(--default-text-color);
  background-color: var(--default-background-color);
`;

const PageWrapper = styled.div`
  max-width: 900px;
  margin: 0 auto;
`;

const App = (props) => {
  const [
    showMenu,
    toggleMenu,
  ] = useState(false);

  return (
    <Router>
      <GlobalStyle />
      <AppWrapper>
        <MessageProvider>
          <UserProvider>
            <Header
              showMenu={ showMenu }
              toggleMenu={ toggleMenu } />
            <SideMenu
              toggleMenu={ toggleMenu }
              showMenu={ showMenu } />
            <Message />
            <Switch>
              <Route
                exact
                path="/">
                <Home />
              </Route>
              <Route
                path="/exposureanalysis">
                <PageWrapper>
                  <AthenaApp />
                </PageWrapper>
              </Route>
              <Route
                path="/incomesim">
                <PageWrapper>
                  <AntevortaApp />
                </PageWrapper>
              </Route>
              <Route
                path="/backtest">
                <PageWrapper>
                  <AphroditeApp />
                </PageWrapper>
              </Route>
            </Switch>
          </UserProvider>
        </MessageProvider>
      </AppWrapper>
    </Router>
  );
};

import {
  render,
} from 'react-dom';

const appEl = document.getElementById('app');
render(<App />, appEl);
