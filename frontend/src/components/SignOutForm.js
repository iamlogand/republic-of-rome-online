import { Component } from 'react';

class SignInForm extends Component {
  constructor(props) {
    super(props);

    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleSubmit(event) {
    event.preventDefault();
    this.props.setAuthData({
      accessToken: '',
      refreshToken: '',
      username: ''
    });
  }

  render() {
    return (
      <form onSubmit={this.handleSubmit} className="auth_form">
        <div>
          <div className='auth_prompt'>Are you sure you want to sign out?</div>
          <input className="auth_submit auth_submit_ready" type="submit" value="Yes" />
        </div>
      </form>
    );
  }
}

export default SignInForm;
