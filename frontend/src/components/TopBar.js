import "./TopBar.css";
import { Link } from "react-router-dom";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faUser } from '@fortawesome/free-solid-svg-icons'

export default function TopBar(props) {

  let userArea;
  const username = props.username;
  if (username === '') {
    userArea =
      <div><Link className="plainlink" to="/auth/sign-in">Sign in</Link></div>
  } else {
    userArea =
      <div>
        <Link className="plainlink topbar_currentuser" to="/auth/account">
          <div className="icon">
            <FontAwesomeIcon icon={faUser} />
          </div>
          <div>
            {username}
          </div>
        </Link>
        <div><Link className="plainlink" to="/auth/sign-out">Sign Out</Link></div>
      </div>;
  }

  return (
    <div className="topbar_container">
      <div className="topbar">
        <div className="topbar_title">
          <Link className="plainlink" to="/">Republic of Rome Online</Link>
        </div>
        <div className="topbar_info">{userArea}</div>
      </div>
    </div>
  )
}
