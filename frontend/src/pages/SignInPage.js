import SignInForm from "../components/SignInForm.js";
import RegisterForm from "../components/RegisterForm.js";
import "../css/Authentication.css";
import { Component } from 'react';

class SignInPage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      signInActive: '',
      registerActive: ''
    };
  }

  render() {
    return (
      <div className="autharea">
        <div>
          <div>
            <div className="box">
              <div className="title">Sign In</div>
              <SignInForm setAuthData={this.props.setAuthData} />
            </div>
          </div>
          <div>
            <div className="box">
              <div className="title">Register</div>
              <RegisterForm setAuthData={this.props.setAuthData} />
            </div>
          </div>
        </div>
      </div>
    )
  }
}

export default SignInPage;