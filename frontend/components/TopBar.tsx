import Link from "next/link";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faUser } from '@fortawesome/free-solid-svg-icons'
import { useAuth } from "../contexts/ContextProvider";
import styles from './TopBar.module.css';
import Button from "./Button";

interface TopBarProps {
  setDialog: Function
}

/**
 * The component at the top of the page containing the "Republic of Rome Online" title
 */
const TopBar = (props: TopBarProps) => {
  const { username } = useAuth();
  
  const handleSignIn = () => {
    props.setDialog('sign-in')
  }

  const handleSignOut = () => {
    props.setDialog('sign-out')
  }

  return (
    <header className={styles.topBar} role="banner" aria-label="Website Header">
      <Link href="/" className="no-decor inherit-color" ><h1>Republic of Rome Online</h1></Link>
      {username ?
        <nav aria-label="User Navigation">
          <Button href="/account" styleType="topBar" maxWidth={280}>
            <FontAwesomeIcon icon={faUser} style={{ marginRight: "10px" }} height={16} width={16} />
            <span className="no-wrap-ellipsis">{username}</span>
          </Button>
          <Button onClick={handleSignOut} styleType="topBar">Sign out</Button>
        </nav>
        :
        <nav aria-label="User Navigation">
          <Button onClick={handleSignIn} styleType="topBar">Sign in</Button>
        </nav>
      }
    </header>
  )
}

export default TopBar
