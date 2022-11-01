import SignInForm from "../components/SignInForm.js";
import "../css/SignInAndOutPages.css";

export default function SignInPage(props) {
  return (
    <div className="autharea">
      <div>
        <div className="box">
          <div className="title">Sign In</div>
          <SignInForm
            setAuthData={props.setAuthData} />
        </div>
      </div>
    </div>
  )
}