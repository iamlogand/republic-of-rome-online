import "./TopBar.css";
import { Link } from "react-router-dom";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faUser } from '@fortawesome/free-solid-svg-icons'

interface TopBarProps {
  username: string,
  setDialog: Function
}

/**
 * The component at the top of the page containing the "Republic of Rome Online" title
 */
const TopBar = (props: TopBarProps) => {
  
  const handleSignIn = () => {
    props.setDialog('sign-in')
  }

  const handleSignOut = () => {
    props.setDialog('sign-out')
  }

  return (
    <header className="top-bar" role="banner" aria-label="Website Header">
      <Link to="/" className="no-decor inherit-color" ><h1>Republic of Rome Online</h1></Link>
      {props.username ?
        <nav aria-label="User Navigation">
          <Link to="/account" className="button inherit-color" style={{padding: "0 10px", maxWidth: "300px"}} aria-label="Your Account">
            <FontAwesomeIcon icon={faUser} style={{ marginRight: "10px" }} />
            <span className="sr-only">User: </span>
            <span className="no-wrap-ellipsis">{props.username}</span>
          </Link>
          <button onClick={handleSignOut} className="button" style={{width: "85px"}}>Sign out</button>
        </nav>
        :
        <nav aria-label="User Navigation">
          <button onClick={handleSignIn} className="button" style={{width: "80px"}}>Sign in</button>
        </nav>
      }
    </header>
  )
}

export default TopBar
