import { ReactNode, createContext, useContext } from "react"
import useCookies from "../hooks/useCookies"
import User from "@/classes/User"
import { deserializeToInstance } from "@/functions/serialize"

interface AuthContextType {
  accessToken: string
  setAccessToken: (value: string) => void
  refreshToken: string
  setRefreshToken: (value: string) => void
  user: User | null
  setUser: (value: User | null) => void
  darkMode: boolean
  setDarkMode: (value: boolean) => void
}

const AuthContext = createContext<AuthContextType | null>(null)

export const useAuthContext = (): AuthContextType => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error("useAuthContext must be used within an AuthProvider")
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
  pageProps: any
}

export const AuthProvider = (props: AuthProviderProps) => {
  const clientAccessToken = props.pageProps.clientAccessToken ?? ""
  const clientRefreshToken = props.pageProps.clientRefreshToken ?? ""
  const clientUserJSON = props.pageProps.clientUser ?? ""

  const [accessToken, setAccessToken] = useCookies<string>(
    "accessToken",
    clientAccessToken
  )
  const [refreshToken, setRefreshToken] = useCookies<string>(
    "refreshToken",
    clientRefreshToken
  )

  const [user, setUser] = useCookies<string>("user", clientUserJSON)
  let parsedUser: User | null
  if (user) {
    // This needs to be parsed twice for some reason,
    // possibly because of how cookies are serialized
    parsedUser = deserializeToInstance<User>(User, JSON.parse(user))
  } else {
    parsedUser = null
  }
  const storeUser = (user: User | null) => setUser(JSON.stringify(user))

  const [darkMode, setDarkMode] = useCookies<boolean>("darkMode", false)
  let parsedDarkMode: boolean
  if (darkMode) {
    parsedDarkMode = JSON.parse(darkMode)
  } else {
    parsedDarkMode = false
  }
  const storeDarkMode = (darkMode: boolean) =>
    setDarkMode(JSON.stringify(darkMode))

  return (
    <AuthContext.Provider
      value={{
        accessToken,
        setAccessToken,
        refreshToken,
        setRefreshToken,
        user: parsedUser,
        setUser: storeUser,
        darkMode: parsedDarkMode,
        setDarkMode: storeDarkMode,
      }}
    >
      {props.children}
    </AuthContext.Provider>
  )
}
