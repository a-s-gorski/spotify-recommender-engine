import Keycloak from 'keycloak-js';
import type { KeycloakConfig } from 'keycloak-js';

const initOptions: KeycloakConfig = {
  url: import.meta.env.VITE_KEYCLOAK_URL,
  realm: import.meta.env.VITE_KEYCLOAK_REALM,
  clientId: import.meta.env.VITE_KEYCLOAK_CLIENT_ID,
};

const keycloak = new Keycloak(initOptions);

let isInitialized = false;

export const initKeycloak = () => {
  if (!isInitialized) {
    isInitialized = true;
    return keycloak.init({
      onLoad: 'check-sso',
      pkceMethod: 'S256',
      silentCheckSsoRedirectUri: window.location.origin + '/silent-check-sso.html',
      checkLoginIframe: false,
    });
  }
  return Promise.resolve(keycloak.authenticated ?? false);
};

export default keycloak;
