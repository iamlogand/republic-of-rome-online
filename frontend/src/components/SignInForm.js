import { Component } from 'react';
import axios from "axios";

class SignInForm extends Component {
  constructor(props) {
    super(props);
    this.state = {
      username: '',
      password: '',
      feedback: '',
      pending: false,
      submitReady: true
    };

    this.handleInputChange = this.handleInputChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleInputChange(event) {
    if (event.target.name === 'username') {
      this.setState({ username: event.target.value });
    } else if (event.target.name === "password") {
      this.setState({ password: event.target.value });
    }
  }

  handleSubmit(event) {
    event.preventDefault();

    this.setState({
      pending: true,
      submitReady: false
    });

    setTimeout(() => {
      const username = this.state.username;
      const password = this.state.password;

      if (username === '' || password === '') {
        this.setState({
          feedback: 'Please provide your username and password.'
        });
      } else {

        const data = JSON.stringify({
          "username": username,
          "password": password
        });

        axios.post(process.env.REACT_APP_BACKEND_ORIGIN + '/rorapp/api/token/', data, {
          headers: { "Content-Type": "application/json" }
        }).then(response => {
          this.props.setAuthData({
            accessToken: response.data.access,
            refreshToken: response.data.refresh,
            username: username
          });
        }).catch(error => {
          console.log(error);
          if (error.code === "ERR_BAD_REQUEST") {
            this.setState({
              password: '',
              feedback: 'Your username and password do not match. Please try again.'
            });
          } else {
            this.setState({
              password: '',
              feedback: 'Something went wrong. Please try again later.'
            });
          }
        });
      }
      this.setState({
        pending: false,
        submitReady: true
      });
    }, 1);
  }

  renderFeedback = () => {
    if (this.state.feedback !== '') {
      return <div className={`feedback ${this.state.pending ? "" : "feedback-ready"}`}>
        {this.state.feedback}
      </div>
    } else {
      return null
    }
  }

  render() {
    return (
      <form onSubmit={this.handleSubmit} className="form">
        {this.renderFeedback()}
        <div className="field">
          <label htmlFor="username">Username</label>
          <input
            type="text"
            id="username"
            name="username"
            autoComplete="username"
            value={this.state.username}
            onChange={this.handleInputChange} />
        </div>
        <div className="field">
          <label htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            name="password"
            autoComplete="current-password"
            value={this.state.password}
            onChange={this.handleInputChange} />
        </div>
        <div>
          {this.state.submitReady === true
            ? <input className="submit submit-ready" type="submit" value="Sign In" />
            : <div className="submit submit-loading"><img src={require("../images/throbber_light.gif")} alt="loading" /></div>
          }
        </div>
      </form>
    );
  }
}

export default SignInForm;