import { Component } from 'react';
import request from "../helpers/RequestHelper.js"
import "./AccountPage.css";
import TopBar from "../components/TopBar.js"

/**
 * The component for the account page
 */
class AccountPage extends Component {
  constructor(props) {
    super(props);
    this.state = { email: '' };
    this.componentDidMount = this.componentDidMount.bind(this);
  }

  async componentDidMount() {

    // Get the current user's email
    const response = await request('get', 'user/detail/', this.props.accessToken, this.props.refreshToken, this.props.setAuthData);
    if (response) {
      this.setState({ email: response.data.email });
    }
  }

  render() {
    return (
      <div id="page_container">
        <TopBar username={this.props.username} />
        <div id="standard_page">
          <div id="page_content">
            <h1>Account Configuration</h1>
            <p>Manage your account settings here.</p>

            <div className="accountpage_info">
              <div>Username</div>
              <div>{this.props.username}</div>
            </div>
            <div className="accountpage_info">
              <div>Email</div>
              <div>{this.state.email}</div>
            </div>
          </div>
        </div>
      </div>
    );
  }
}

export default AccountPage;
