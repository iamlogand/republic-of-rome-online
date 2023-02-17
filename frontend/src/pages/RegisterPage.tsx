import RegisterForm from "../components/RegisterForm";
import "../css/Auth.css";
import { Link } from "react-router-dom";
import TopBar from "../components/TopBar"

interface RegisterPageProps {
  username: string,
  setAuthData: Function
}

/**
 * The component for the register page, which contains the `RegisterForm` component
 * Currently unfinished
 */
const RegisterPage = (props: RegisterPageProps) => {

  return (
    <div id="page_container">
      <TopBar username={props.username} />
      <div className="auth_area">
        <div>
          <div>
            <div className='auth_box'>
              <div className="auth_title_container">
                <div className="auth_title">Register</div>
                <div className="auth_link">Already have an account? <Link to="/auth/sign-in" className="underlinedlink">Sign in</Link></div>
              </div>
              <RegisterForm setAuthData={props.setAuthData} />
            </div>
          </div>
        </div>
        <div className="auth_spacer"></div>
      </div>
    </div>
  )
}

export default RegisterPage;
