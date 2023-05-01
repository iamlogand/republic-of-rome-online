import Link from "@/components/Link";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faUser } from '@fortawesome/free-solid-svg-icons'
import { useAuthContext } from "../contexts/AuthContext";
import styles from './TopBar.module.css';
import Button from "./Button";
import { useModalContext } from "@/contexts/ModalContext";

interface TopBarProps {
  ssrEnabled: boolean;
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

  // This is where the `ssrEnabled` page prop is used. To prevent hydration issues,
  // the TopBar will render a generic version of itself if `ssrEnabled` is undefined.
  // The only page where SSR should not be enabled is the 404 page.
  return (
    <header className={styles.topBar} role="banner" aria-label="Website Header">
      <Link href="/" inheritStyle={true}><h1>Republic of Rome Online</h1></Link>
      {props.ssrEnabled &&
        <>
          {username ?
            <nav aria-label="User Navigation">
              <Button href="/account" styleType="topBar" maxWidth={280}>
                <FontAwesomeIcon icon={faUser} style={{ marginRight: "8px" }} height={14} width={14} />
                <span className="no-wrap-ellipsis">{username}</span>
              </Button>
              <Button onClick={handleSignOut} styleType="topBar">Sign out</Button>
            </nav>
            :
            <nav aria-label="User Navigation">
              <Button onClick={handleSignIn} styleType="topBar">Sign in</Button>
            </nav>
          }
        </>
      }
    </header>
  )
}

export default TopBar
