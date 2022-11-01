import "./TopBar.css";
import { Link } from "react-router-dom";

export default function TopBar(props) {

  let userArea;
  const username = props.username;
  if (username === '') {
    userArea =
      <div className="topbar_info">
        <div><Link className="plainlink" to="auth/sign-in">Sign in</Link></div>
      </div>;
  } else {
    userArea = 
      <div className="topbar_info">
        <div className="topbar_info_currentuser">
          <div>
            Signed in as:
          </div>
          <div className="topbar_info_currentuser_name">
            {username}
          </div>
        </div>
        <div><Link className="plainlink" to="auth/sign-out">Sign Out</Link></div>
      </div>;
  }

  return (
    <div className="topbar">
      <div className="topbar_title">
        <Link className="plainlink" to="/">Republic of Rome Online</Link>
      </div>
      {userArea}
    </div>
  )
}
