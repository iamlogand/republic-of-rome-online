import SignOutForm from "../components/SignOutForm";
import TopBar from "../components/TopBar"

interface SignOutPageProps {
  username: string,
  setAuthData: Function
}

/**
 * The component for the sign out page, which contains the `SignOutForm` component
 */
const SignOutPage = (props: SignOutPageProps) => {
  return (
    <div id="page_container">
      <TopBar username={props.username} />
      <div className="auth_area">
        <div>
          <div>
            <div className="auth_box">
              <div className="auth_title_container"><div className="auth_title">Sign Out</div></div>
              <SignOutForm setAuthData={props.setAuthData} />
            </div>
          </div>
        </div>
        <div className="auth_spacer"></div>
      </div>
    </div>
  );
}

export default SignOutPage;
