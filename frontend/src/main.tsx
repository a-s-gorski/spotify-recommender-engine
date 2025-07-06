import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { KeycloakProvider } from './KeycloakProvider';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <KeycloakProvider>
      <App />
    </KeycloakProvider>
  </React.StrictMode>
);
