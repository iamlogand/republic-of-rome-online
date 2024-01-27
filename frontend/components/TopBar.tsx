import { useState } from "react"
import Link from "next/link"
import Image from "next/image"
import { useRouter } from "next/router"
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
} from "@mui/material"
import PersonIcon from "@mui/icons-material/Person"
import LightModeIcon from "@mui/icons-material/LightMode"
import DarkModeIcon from "@mui/icons-material/DarkMode"

import { useAuthContext } from "@/contexts/AuthContext"
import SiteLogo from "@/images/siteLogo.png"
import { ThemeProvider } from "@emotion/react"
import darkTheme from "@/themes/darkTheme"
import rootTheme from "@/themes/rootTheme"

interface TopBarProps {
  ssrEnabled: boolean
}

// The component at the top of the page containing the "Republic of Rome Online" title
const TopBar = (props: TopBarProps) => {
  const {
    user,
    setAccessToken,
    setRefreshToken,
    setUser,
    darkMode,
    setDarkMode,
  } = useAuthContext()
  const router = useRouter()

  const [dialogOpen, setDialogOpen] = useState(false)

  const handleSignOut = async () => {
    setAccessToken("")
    setRefreshToken("")
    setUser(null)
    setDialogOpen(false)
    await router.push("/") // Navigate to home
  }

  const toggleDarkMode = () => {
    setDarkMode(!darkMode)
  }

  // This is where the `ssrEnabled` page prop is used. To prevent hydration issues,
  // the TopBar will render a generic version of itself if `ssrEnabled` is falsy.
  // The only page where SSR should not be enabled is the 404 page.
  return (
    <header
      className="w-full box-border px-8 py-3 text-white bg-tyrian-700 flex flex-col sm:flex-row justify-between items-center gap-3"
      role="banner"
      aria-label="Website Header"
    >
      <Button
        color="inherit"
        LinkComponent={Link}
        href="/"
        className="flex flex-col sm:flex-row gap-3"
        sx={{ paddingTop: 0, paddingBottom: 0 }}
      >
        <Image
          src={SiteLogo}
          alt="Site logo"
          height={38}
          className="border-solid border border-tyrian-300 rounded"
        />
        <h1
          className="text-2xl text-center tracking-tight text-tyrian-50 flex"
          style={{ fontFamily: "var(--font-trajan)" }}
        >
          Republic of Rome Online
        </h1>
      </Button>
      <div className="flex items-center gap-3">
        <IconButton
          onClick={toggleDarkMode}
          aria-label={`enable ${darkMode ? "light" : "dark"} mode`}
        >
          {darkMode ? (
            <LightModeIcon className="text-white" />
          ) : (
            <DarkModeIcon className="text-white" />
          )}
        </IconButton>
        {props.ssrEnabled &&
          (user ? (
            <nav className="flex gap-3 items-stretch">
              <IconButton
                LinkComponent={Link}
                href="/account"
                aria-label="account"
              >
                <PersonIcon className="text-white" />
              </IconButton>
              <Button
                onClick={() => setDialogOpen(true)}
                color="primary"
                sx={{ color: "white" }}
              >
                Sign out
              </Button>
            </nav>
          ) : (
            <nav className="flex items-center">
              <Button
                LinkComponent={Link}
                href={`/sign-in?redirect=${router.asPath}`}
                color="primary"
                sx={{ color: "white" }}
              >
                Sign in
              </Button>
            </nav>
          ))}
      </div>
      <ThemeProvider theme={darkMode ? darkTheme : rootTheme}>
        <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
          <DialogTitle>Sign out</DialogTitle>
          <DialogContent>Are you sure you want to sign out?</DialogContent>
          <DialogActions>
            <Button onClick={() => setDialogOpen(false)} color="primary">
              Cancel
            </Button>
            <Button onClick={handleSignOut} color="primary">
              Yes
            </Button>
          </DialogActions>
        </Dialog>
      </ThemeProvider>
    </header>
  )
}

export default TopBar
