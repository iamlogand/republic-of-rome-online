import { Component } from 'react';
import request from "../helpers/RequestHelper.js"
import "./AccountPage.css";

class AccountPage extends Component {
  constructor(props) {
    super(props);
    this.state = { email: '' };
    this.componentDidMount = this.componentDidMount.bind(this);
  }

  async componentDidMount() {
    const response = await request('get', 'user/detail/', this.props.accessToken, this.props.refreshToken, this.props.setAuthData);
    if (response) {
      this.setState({ email: response.data.email });
    }
  }

  render() {
    return (
      <div>
        <h1>Account Configuration</h1>
        <p>Manage your account settings here.</p>

        <div className="account_info">
          <div>Username</div>
          <div>{this.props.username}</div>
        </div>
        <div className="account_info">
          <div>Email</div>
          <div>{this.state.email}</div>
        </div>
      </div>
    );
  }
}

export default AccountPage;
