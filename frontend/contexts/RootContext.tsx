import React, { createContext, useContext } from 'react';
import { AuthProvider } from './AuthContext';
import { DialogProvider } from './DialogContext';

const RootContext = createContext({});

export const useRootContext = () => {
  return useContext(RootContext);
};

interface RootProviderProps {
  children: React.ReactNode;
  pageProps: any;
}

export const RootProvider = (props: RootProviderProps) => {
  return (
    <RootContext.Provider value={{}}>
      <AuthProvider pageProps={props.pageProps}>
        <DialogProvider>
          {props.children}
        </DialogProvider>
      </AuthProvider>
    </RootContext.Provider>
  );
};
