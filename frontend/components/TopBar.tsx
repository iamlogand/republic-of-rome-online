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

import { useAuthContext } from "@/contexts/AuthContext"
import SiteLogo from "@/images/siteLogo.png"

interface TopBarProps {
  ssrEnabled: boolean
}

// The component at the top of the page containing the "Republic of Rome Online" title
const TopBar = (props: TopBarProps) => {
  const { user, setAccessToken, setRefreshToken, setUser } = useAuthContext()
  const router = useRouter()

  const [dialogOpen, setDialogOpen] = useState(false)

  const handleSignOut = async () => {
    setAccessToken("")
    setRefreshToken("")
    setUser(null)
    setDialogOpen(false)
    await router.push("/") // Navigate to home
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
        className="py-0 flex flex-col sm:flex-row gap-3"
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
      {props.ssrEnabled && (
        <div className="flex items-center">
          {user ? (
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
                variant="contained"
                LinkComponent={Link}
                href={`/sign-in?redirect=${router.asPath}`}
              >
                Sign in
              </Button>
            </nav>
          )}
        </div>
      )}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
        <DialogTitle>Sign out</DialogTitle>
        <DialogContent className="text-stone-500">
          Are you sure you want to sign out?
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)} color="primary">
            Cancel
          </Button>
          <Button onClick={handleSignOut} color="primary">
            Yes
          </Button>
        </DialogActions>
      </Dialog>
    </header>
  )
}

export default TopBar
