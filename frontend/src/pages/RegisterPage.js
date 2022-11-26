import RegisterForm from "../components/RegisterForm.js";
import "../css/Auth.css";
import { Component } from 'react';
import { Link } from "react-router-dom";
import TopBar from "../components/TopBar.js"

class RegisterPage extends Component {

  render() {
    return (
      <div id="page_container">
        <TopBar username={this.props.username} />
        <div className="auth_area">
          <div>
            <div>
              <div className='auth_box'>
                <div className="auth_title_container">
                  <div className="auth_title">Register</div>
                  <div className="auth_link">Already have an account? <Link to="/auth/sign-in" className="inheritcolor">Sign in</Link></div>
                </div>
                <RegisterForm setAuthData={this.props.setAuthData} active={this.props.registerActive} />
              </div>
            </div>
          </div>
          <div className="auth_spacer"></div>
        </div>
      </div>
    )
  }
}

export default RegisterPage;
