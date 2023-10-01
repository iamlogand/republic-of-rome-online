import Link from 'next/link'
import Image from 'next/image'
import { useRouter } from 'next/router'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faUser } from '@fortawesome/free-solid-svg-icons'
import { Button, Stack, ThemeProvider }  from '@mui/material'

import { useAuthContext } from "@/contexts/AuthContext"
import { useModalContext } from "@/contexts/ModalContext"
import styles from './TopBar.module.css'
import frameTheme from "@/themes/frameTheme"
import SiteLogo from "@/images/siteLogo.png"

interface TopBarProps {
  ssrEnabled: boolean
}

// The component at the top of the page containing the "Republic of Rome Online" title
const TopBar = (props: TopBarProps) => {
  const { user } = useAuthContext()
  const { setModal } = useModalContext()
  const router = useRouter()

  const handleSignOut = () => {
    setModal('sign-out')
  }

  // This is where the `ssrEnabled` page prop is used. To prevent hydration issues,
  // the TopBar will render a generic version of itself if `ssrEnabled` is falsy.
  // The only page where SSR should not be enabled is the 404 page.
  return (
    <ThemeProvider theme={frameTheme}>
      <header className={styles.topBar} role="banner" aria-label="Website Header">
        <Stack
          direction={{ xs: 'column', md: 'row' }}
          spacing={{ xs: 1 }}
          justifyContent="space-between"
          alignItems={{ xs: 'stretch', md: 'center' }}
          marginBottom={{ xs: 1, md: "0" }}
        >
          <Button color="inherit" LinkComponent={Link} href="/" style={{padding: "0"}}>
            <Image src={SiteLogo} alt="Site logo" height={36} className={styles.siteLogo} />
            <h1>Republic of Rome Online</h1>
          </Button>
          {props.ssrEnabled &&
            <>
              {user ?
                <nav aria-label="User Navigation">
                  <Stack direction={{ xs: 'column', sm: 'row' }} spacing={{ xs: 2 }} justifyContent="center">
                    <Button variant="outlined" style={{textTransform: "none"}} LinkComponent={Link} href="/account">
                      <FontAwesomeIcon icon={faUser} style={{ marginRight: "8px" }} height={16} width={16} />
                      <span className="no-wrap-ellipsis">{user.username}</span>
                    </Button>
                    <Button variant="outlined" onClick={handleSignOut}>Sign out</Button>
                  </Stack>
                </nav>
                :
                <nav aria-label="User Navigation">
                  <Stack direction={{ xs: 'column', sm: 'row' }} spacing={{ xs: 2 }} justifyContent="center">
                    <Button variant="outlined" LinkComponent={Link} href={`/sign-in?redirect=${router.asPath}`}>Sign in</Button>
                  </Stack>
                </nav>
              }
            </>
          }
        </Stack>
      </header>
    </ThemeProvider>
  )
}

export default TopBar
