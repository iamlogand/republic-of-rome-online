import SignOutForm from "../components/SignOutForm.js";
import "../css/SignInAndOutPages.css";

export default function SignOutPage(props) {
  return (
    <div className="autharea">
      <div>
        <div className="box">
          <div className="title">Sign Out</div>
          <div>Are you sure you want to sign out?</div>
          <SignOutForm
            setAuthData={props.setAuthData} />
        </div>
      </div>
    </div>
  );
}