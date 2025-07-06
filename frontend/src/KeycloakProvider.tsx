import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import keycloak, { initKeycloak } from './keycloak';

interface KeycloakContextType {
  keycloak: typeof keycloak;
  authenticated: boolean;
  loading: boolean;
}

const KeycloakContext = createContext<KeycloakContextType | undefined>(undefined);

export const useKeycloak = () => {
  const context = useContext(KeycloakContext);
  if (!context) throw new Error("useKeycloak must be used within a KeycloakProvider");
  return context;
};

export const KeycloakProvider = ({ children }: { children: ReactNode }) => {
  const [authenticated, setAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    initKeycloak()
      .then((auth: any) => {
        setAuthenticated(auth);
        setLoading(false);
      })
      .catch(() => {
        setAuthenticated(false);
        setLoading(false);
      });
  }, []);

  return (
    <KeycloakContext.Provider value={{ keycloak, authenticated, loading }}>
      {children}
    </KeycloakContext.Provider>
  );
};
