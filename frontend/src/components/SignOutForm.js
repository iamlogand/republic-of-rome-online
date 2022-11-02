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
      <form onSubmit={this.handleSubmit}>
        <div>
          <input className="submit" type="submit" value="Yes" />
        </div>
      </form>
    );
  }
}

export default SignInForm;