import { createContext, useContext } from 'react';
import useLocalStorage from './helpers/useLocalStorage';

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

export const AuthProvider = ({ children }: React.PropsWithChildren<{}>) => {
  const [accessToken, setAccessToken] = useLocalStorage<string>('accessToken', '');
  const [refreshToken, setRefreshToken] = useLocalStorage<string>('refreshToken', '');
  const [username, setUsername] = useLocalStorage<string>('username', '');

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
      {children}
    </AuthContext.Provider>
  );
};
