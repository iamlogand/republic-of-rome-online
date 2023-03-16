import "./TopBar.css";
import { Link } from "react-router-dom";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faUser } from '@fortawesome/free-solid-svg-icons'

interface TopBarProps {
  username: string
}

/**
 * The component at the top of the page containing the "Republic of Rome Online" title
 */
const TopBar = (props: TopBarProps) => {
  return (
    <nav className="top-bar">
      <div>
        <h1><Link className="no-decor inherit-color" to="/">Republic of Rome Online</Link></h1>
      </div>
      {props.username ?
        <div>
          <Link className="no-decor inherit-color" to="/account">
              <FontAwesomeIcon icon={faUser} style={{marginRight: "10px"}}/>{props.username}
          </Link>
          <Link className="no-decor inherit-color" to="/sign-out">Sign Out</Link>
        </div> :
        <Link className="no-decor inherit-color" to="/sign-in">Sign in</Link>}
    </nav>
  )
}

export default TopBar
