import SignInForm from "../components/SignInForm.js";
import RegisterForm from "../components/RegisterForm.js";
import "../css/Authentication.css";
import { Component } from 'react';

class SignInPage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      signInActive: true,
      registerActive: true
    };
  }

  handleClick = (activeForm) => {
    if (activeForm === 'signIn') {
      this.setState({signInActive: true, registerActive: false})
    } else if (activeForm === 'register') {
      this.setState({signInActive: false, registerActive: true})
    }
  } 

  render() {
    return (
      <div className="autharea">
        <div>
          <div>
            <div className={`box ${this.state.signInActive ? '' : 'innactive'}`} onClick={() => this.handleClick('signIn')} >
              <div className="title">Sign In</div>
              <SignInForm setAuthData={this.props.setAuthData} active={this.props.signInActive} />
            </div>
          </div>
          <div>
            <div className={`box ${this.state.registerActive ? '' : 'innactive'}`} onClick={() => this.handleClick('register')} >
              <div className="title"><div>New here?</div>Register</div>
              <RegisterForm setAuthData={this.props.setAuthData} active={this.props.registerActive} />
            </div>
          </div>
        </div>
      </div>
    )
  }
}

export default SignInPage;