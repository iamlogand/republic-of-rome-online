import { ReactNode, createContext, useContext } from 'react';
import useCookies from '../hooks/useCookies';

interface AuthContextType {
  accessToken: string;
  refreshToken: string;
  username: string;
  setAccessToken: (value: string) => void;
  setRefreshToken: (value: string) => void;
  setUsername: (value: string) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode,
  pageProps: any
}

export const AuthProvider = ( props: AuthProviderProps ) => {

  const ssrAccessToken = props.pageProps.ssrAccessToken ?? "";
  const ssrRefreshToken = props.pageProps.ssrRefreshToken ?? "";
  const ssrUsername = props.pageProps.ssrUsername ?? "";

  const [accessToken, setAccessToken] = useCookies<string>('accessToken', ssrAccessToken);
  const [refreshToken, setRefreshToken] = useCookies<string>('refreshToken', ssrRefreshToken);
  const [username, setUsername] = useCookies<string>('username', ssrUsername);

  return (
    <AuthContext.Provider
      value={{
        accessToken,
        refreshToken,
        username,
        setAccessToken,
        setRefreshToken,
        setUsername,
      }}
    >
      {props.children}
    </AuthContext.Provider>
  );
};
