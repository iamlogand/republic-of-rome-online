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
        <div className="autharea">
          <div>
            <div>
              <div className='box'>
                <div className="title-space">
                  <div className="title">Register</div>
                  <div className="link">Already have an account? <Link to="/auth/sign-in" className="underlinedlink">Sign in</Link></div>
                </div>
                <RegisterForm setAuthData={this.props.setAuthData} active={this.props.registerActive} />
              </div>
            </div>
          </div>
          <div className="spacer"></div>
        </div>
      </div>
    )
  }
}

export default RegisterPage;
