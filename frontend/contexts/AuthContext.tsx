import { ReactNode, createContext, useContext } from 'react';
import useCookies from '../hooks/useCookies';
import User from '@/classes/User';
import { deserializeToInstance } from '@/functions/serialize';

interface AuthContextType {
  accessToken: string;
  refreshToken: string;
  user: User | undefined;
  setAccessToken: (value: string) => void;
  setRefreshToken: (value: string) => void;
  setUser: (value: User | undefined) => void;
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
  const clientUserJSON = props.pageProps.clientUser ?? "";

  const [accessToken, setAccessToken] = useCookies<string>('accessToken', clientAccessToken);
  const [refreshToken, setRefreshToken] = useCookies<string>('refreshToken', clientRefreshToken);
  const [user, setUser] = useCookies<string>('user', clientUserJSON);

  let parsedUser: User | undefined;
  if (user) {
    // This needs to be parsed twice for some reason,
    // possibly because of how cookies are serialized
    parsedUser = deserializeToInstance<User>(User, JSON.parse(user))  
  } else {
    parsedUser = undefined;
  }

  const storeUser = (user: User | undefined) => setUser(JSON.stringify(user))

  return (
    <AuthContext.Provider value={{ accessToken, refreshToken, user: parsedUser, setAccessToken, setRefreshToken, setUser: storeUser }} >
      {props.children}
    </AuthContext.Provider>
  );
};
