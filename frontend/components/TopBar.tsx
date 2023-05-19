import Link from 'next/link';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faUser } from '@fortawesome/free-solid-svg-icons'
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import { ThemeProvider } from '@mui/material/styles';

import { useAuthContext } from "@/contexts/AuthContext";
import { useModalContext } from "@/contexts/ModalContext";
import styles from './TopBar.module.css';
import frameTheme from "@/themes/frameTheme";

interface TopBarProps {
  clientEnabled: boolean;
}

/**
 * The component at the top of the page containing the "Republic of Rome Online" title
 */
const TopBar = (props: TopBarProps) => {
  const { username } = useAuthContext();
  const { setModal } = useModalContext();
  
  const handleSignIn = () => {
    setModal('sign-in')
  }

  const handleSignOut = () => {
    setModal('sign-out')
  }

  // This is where the `clientEnabled` page prop is used. To prevent hydration issues,
  // the TopBar will render a generic version of itself if `clientEnabled` is undefined.
  // The only page where SSR should not be enabled is the 404 page.
  return (
    <ThemeProvider theme={frameTheme}>
      <header className={styles.topBar} role="banner" aria-label="Website Header">
        <Stack direction={{ xs: 'column', md: 'row' }} spacing={{ xs: 1 }} justifyContent="space-between" alignItems={{ xs: 'stretch', md: 'center' }}>
          <Button color="inherit" LinkComponent={Link} href="/" style={{padding: "0"}}><h1>Republic of Rome Online</h1></Button>
          {props.clientEnabled &&
            <>
              {username ?
                <nav aria-label="User Navigation">
                  <Stack direction={{ xs: 'column', sm: 'row' }} spacing={{ xs: 2 }} justifyContent="center">
                    <Button variant="outlined" style={{textTransform: "none"}} LinkComponent={Link} href="/account">
                      <FontAwesomeIcon icon={faUser} style={{ marginRight: "8px" }} height={14} width={14} />
                      <span className="no-wrap-ellipsis">{username}</span>
                    </Button>
                    <Button variant="outlined" onClick={handleSignOut}>Sign out</Button>
                  </Stack>
                </nav>
                :
                <nav aria-label="User Navigation">
                  <Stack direction={{ xs: 'column', sm: 'row' }} spacing={{ xs: 2 }} justifyContent="center">
                    <Button variant="outlined" onClick={handleSignIn}>Sign in</Button>
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
