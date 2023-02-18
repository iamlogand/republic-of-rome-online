import SignInForm from "../components/SignInForm";
import "../css/Auth.css";
import { Link } from "react-router-dom";
import TopBar from "../components/TopBar"

interface SignInPageProps {
  username: string,
  setAuthData: Function
}

/**
 * The component for the sign in page, which contains the `SignInForm` component
 */
const SignInPage = (props: SignInPageProps) => {
  return (
    <div id="page_container">
      <TopBar username={props.username} />
      <div className="auth_area">
        <div>
          <div>
            <div className='auth_box'>
              <div className="auth_title_container">
                <div className="auth_title">Sign in</div>
                <div className="auth_link">New here? <Link to="/auth/register" className="inherit-color">Register a new account</Link></div>
              </div>
              <SignInForm setAuthData={props.setAuthData} />
            </div>
          </div>
        </div>
        <div className="auth_spacer"></div>
      </div>
    </div>
  );
}

export default SignInPage;
