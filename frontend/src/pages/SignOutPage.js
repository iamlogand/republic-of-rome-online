import SignOutForm from "../components/SignOutForm.js";
import "../css/Auth.css";
import { Component } from 'react';
import TopBar from "../components/TopBar.js"

class SignOutPage extends Component {
  render() {
    return (
      <div id="page_container">
        <TopBar username={this.props.username} />
        <div className="autharea">
          <div>
            <div>
              <div className="box">
                <div className="title-space"><div className="title">Sign Out</div></div>
                <SignOutForm setAuthData={this.props.setAuthData} />
              </div>
            </div>
          </div>
          <div className="spacer"></div>
        </div>
      </div>
    );
  }
}

export default SignOutPage;
