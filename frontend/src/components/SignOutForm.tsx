import { Component } from 'react';

/**
 * The component for the sign out form
 */
class SignOutForm extends Component {
  constructor(props) {
    super(props);

    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleSubmit(event) {
    event.preventDefault();  // Prevent default form submission behavior

    // Clear auth data
    this.props.setAuthData({
      accessToken: '',
      refreshToken: '',
      username: ''
    });
  }

  render() {
    return (
      <form onSubmit={this.handleSubmit} className="auth_form">
        <div>Are you sure you want to sign out?</div>
        <input className="auth_submit auth_submit_ready" type="submit" value="Yes" />
      </form>
    );
  }
}

export default SignOutForm;
