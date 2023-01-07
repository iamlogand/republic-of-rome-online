import "./TopBar.css";
import { Link } from "react-router-dom";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faUser } from '@fortawesome/free-solid-svg-icons'

/**
 * The component at the top of the page containing the "Republic of Rome Online" title
 */
export default function TopBar(props) {

  // Assign some JSX to `userArea` for use in the return statement
  let userArea;
  const username = props.username;
  if (username === '') {

    // If the user is signed out, assign a sign in button to `userArea`
    userArea =
      <div><Link className="plainlink" to="/auth/sign-in">Sign in</Link></div>

  } else {

    // If the user is already signed in, assign two items to `userArea`:
    // the account button and a sign out button
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

  // Return the website title and the contents of `userArea`
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
