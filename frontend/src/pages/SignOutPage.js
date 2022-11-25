import SignOutForm from "../components/SignOutForm.js";
import "../css/Auth.css";
import { Component } from 'react';
import TopBar from "../components/TopBar.js"

class SignOutPage extends Component {
  render() {
    return (
      <div id="page_container">
        <TopBar username={this.props.username} />
        <div className="auth_area">
          <div>
            <div>
              <div className="auth_box">
                <div className="auth_title_container"><div className="auth_title">Sign Out</div></div>
                <SignOutForm setAuthData={this.props.setAuthData} />
              </div>
            </div>
          </div>
          <div className="auth_spacer"></div>
        </div>
      </div>
    );
  }
}

export default SignOutPage;
