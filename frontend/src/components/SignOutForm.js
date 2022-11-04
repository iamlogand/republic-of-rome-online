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
      <form onSubmit={this.handleSubmit} className="form">
        <div>
          <div className='prompt'>Are you sure you want to sign out?</div>
          <input className="submit submit-ready" type="submit" value="Yes" />
        </div>
      </form>
    );
  }
}

export default SignInForm;