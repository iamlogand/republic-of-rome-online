import { ReactNode, createContext, useContext } from 'react';
import useCookies from '../hooks/useCookies';

interface ContextType {
  accessToken: string;
  refreshToken: string;
  username: string;
  setAccessToken: (value: string) => void;
  setRefreshToken: (value: string) => void;
  setUsername: (value: string) => void;
}

const Context = createContext<ContextType | undefined>(undefined);

export const useAuth = (): ContextType => {
  const context = useContext(Context);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface ProviderProps {
  children: ReactNode,
  pageProps: any
}

const ContextProvider = ( props: ProviderProps ) => {

  const ssrAccessToken = props.pageProps.ssrAccessToken ?? "";
  const ssrRefreshToken = props.pageProps.ssrRefreshToken ?? "";
  const ssrUsername = props.pageProps.ssrUsername ?? "";

  const [accessToken, setAccessToken] = useCookies<string>('accessToken', ssrAccessToken);
  const [refreshToken, setRefreshToken] = useCookies<string>('refreshToken', ssrRefreshToken);
  const [username, setUsername] = useCookies<string>('username', ssrUsername);

  return (
    <Context.Provider
      value={{
        accessToken,
        setAccessToken,
        refreshToken,
        setRefreshToken,
        username,
        setUsername,
      }}
    >
      {props.children}
    </Context.Provider>
  );
};

export default ContextProvider;
