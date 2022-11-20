import SignOutForm from "../components/SignOutForm.js";
import "../css/Authentication.css";

export default function SignOutPage(props) {
  return (
    <div className="autharea">
      <div>
        <div>
          <div className="box">
            <div className="title-space"><div className="title">Sign Out</div></div>
            <SignOutForm setAuthData={props.setAuthData} />
          </div>
        </div>
      </div>
      <div className="spacer"></div>
    </div>
  );
}