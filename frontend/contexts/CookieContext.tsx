import { ReactNode, createContext, useContext } from "react"
import useCookies from "../hooks/useCookies"
import User from "@/classes/User"
import { deserializeToInstance } from "@/functions/serialize"

interface CookieContextType {
  accessToken: string
  setAccessToken: (value: string) => void
  refreshToken: string
  setRefreshToken: (value: string) => void
  user: User | null
  setUser: (value: User | null) => void
  darkMode: boolean
  setDarkMode: (value: boolean) => void
  groupedSenators: boolean
  setGroupedSenators: (value: boolean) => void
}

const CookieContext = createContext<CookieContextType | null>(null)

export const useCookieContext = (): CookieContextType => {
  const context = useContext(CookieContext)
  if (!context) {
    throw new Error("useCookieContext must be used within a CookieProvider")
  }
  return context
}

interface CookieProviderProps {
  children: ReactNode
  pageProps: any
}

export const CookieProvider = (props: CookieProviderProps) => {
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
  const parsedDarkMode = darkMode ? JSON.parse(darkMode) : false
  const storeDarkMode = (darkMode: boolean) =>
    setDarkMode(JSON.stringify(darkMode))

  // Whether to group senators by faction in the senator list
  const [groupedSenators, setGroupedSenators] = useCookies<boolean>(
    "groupedSenators",
    false
  )
  const parsedGroupedSenators = groupedSenators
    ? JSON.parse(groupedSenators)
    : false
  const storeGroupedSenators = (groupedSenators: boolean) =>
    setGroupedSenators(JSON.stringify(groupedSenators))

  return (
    <CookieContext.Provider
      value={{
        accessToken,
        setAccessToken,
        refreshToken,
        setRefreshToken,
        user: parsedUser,
        setUser: storeUser,
        darkMode: parsedDarkMode,
        setDarkMode: storeDarkMode,
        groupedSenators: parsedGroupedSenators,
        setGroupedSenators: storeGroupedSenators,
      }}
    >
      {props.children}
    </CookieContext.Provider>
  )
}
