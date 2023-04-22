import Link from "next/link";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faUser } from '@fortawesome/free-solid-svg-icons'
import { useAuthContext } from "../contexts/AuthContext";
import styles from './TopBar.module.css';
import Button from "./Button";
import { useModalContext } from "@/contexts/ModalContext";

/**
 * The component at the top of the page containing the "Republic of Rome Online" title
 */
const TopBar = () => {
  const { username } = useAuthContext();
  const { setModal } = useModalContext();
  
  const handleSignIn = () => {
    setModal('sign-in')
  }

  const handleSignOut = () => {
    setModal('sign-out')
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
