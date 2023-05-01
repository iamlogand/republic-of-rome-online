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

export const useAuthContext = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuthContext must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode,
  pageProps: any
}

export const AuthProvider = ( props: AuthProviderProps ) => {

  const clientAccessToken = props.pageProps.clientAccessToken ?? "";
  const clientRefreshToken = props.pageProps.clientRefreshToken ?? "";
  const clientUsername = props.pageProps.clientUsername ?? "";

  const [accessToken, setAccessToken] = useCookies<string>('accessToken', clientAccessToken);
  const [refreshToken, setRefreshToken] = useCookies<string>('refreshToken', clientRefreshToken);
  const [username, setUsername] = useCookies<string>('username', clientUsername);

  return (
    <AuthContext.Provider value={{ accessToken, refreshToken, username, setAccessToken, setRefreshToken, setUsername, }} >
      {props.children}
    </AuthContext.Provider>
  );
};
