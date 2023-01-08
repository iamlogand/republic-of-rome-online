import "./TopBar.css";
import { Link } from "react-router-dom";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faUser } from '@fortawesome/free-solid-svg-icons'

export default function TopBar(props) {

  let userArea;
  const username = props.username;
  if (username === '') {
    userArea =
      <div><Link className="no-decor inherit-color" to="/auth/sign-in">Sign in</Link></div>
  } else {
    userArea =
      <div>
        <Link className="no-decor inherit-color top-bar_current-user" to="/auth/account">
          <div className="icon">
            <FontAwesomeIcon icon={faUser} />
          </div>
          <div>
            {username}
          </div>
        </Link>
        <div><Link className="no-decor inherit-color" to="/auth/sign-out">Sign Out</Link></div>
      </div>;
  }

  return (
    <div className="top-bar_container">
      <div className="top-bar">
        <div className="top-bar_title">
          <Link className="no-decor inherit-color" to="/">Republic of Rome Online</Link>
        </div>
        <div className="top-bar_info">{userArea}</div>
      </div>
    </div>
  )
}
