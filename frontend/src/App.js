import { Component } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home.js";
import JoinGame from "./pages/JoinGame.js";
import RegisterPage from "./pages/RegisterPage.js";
import SignInPage from "./pages/SignInPage.js";
import SignOutPage from "./pages/SignOutPage.js";
import AccountPage from "./pages/AccountPage.js";
import TopBar from "./components/TopBar.js"
import { Navigate } from "react-router-dom";

class App extends Component {
  constructor(props) {
    super(props);

    this.state = {
      accessToken: localStorage.getItem("accessToken") ?? '',
      refreshToken: localStorage.getItem("refreshToken") ?? '',
      username: localStorage.getItem("username") ?? ''
    };
  }

  setAuthData = (data) => {
    if (data.accessToken === '') {
      this.setState({ accessToken: '' });
      localStorage.setItem('accessToken', '');
    } else if (data.accessToken) {
      this.setState({ accessToken: data.accessToken });
      localStorage.setItem('accessToken', data.accessToken);
    }
    if (data.refreshToken === '') {
      this.setState({ refreshToken: '' });
      localStorage.setItem('refreshToken', '');
    } else if (data.refreshToken) {
      this.setState({ refreshToken: data.refreshToken });
      localStorage.setItem('refreshToken', data.refreshToken);
    }
    if (data.username === '') {
      this.setState({ username: '' });
      localStorage.setItem('username', '');
    } else if (data.username) {
      this.setState({ username: data.username });
      localStorage.setItem('username', data.username);
    }
  }

  render() {
    return (
      <BrowserRouter>
        <TopBar username={this.state.username} />
        <Routes>
          <Route index element={<Home />} />
          <Route path="join-game" element={this.state.username === ""
            ? <Navigate to='/auth/sign-in' />
            : <JoinGame
              accessToken={this.state.accessToken}
              refreshToken={this.state.refreshToken}
              setAuthData={this.setAuthData} />} />
          <Route path="auth">
            <Route path="register" element={this.state.username === ""
              ? <RegisterPage setAuthData={this.setAuthData} />
              : <Navigate to='/' />} />
            <Route path="sign-in" element={this.state.username === ""
              ? <SignInPage setAuthData={this.setAuthData} />
              : <Navigate to='/' />} />
            <Route path="sign-out" element={this.state.username === ""
              ? <Navigate to='/' />
              : <SignOutPage setAuthData={this.setAuthData} />} />
            <Route path="account" element={this.state.username === ""
              ? <Navigate to='/' />
              : <AccountPage
                accessToken={this.state.accessToken}
                refreshToken={this.state.refreshToken}
                username ={this.state.username}
                setAuthData={this.setAuthData} />} />
          </Route>
        </Routes>
      </BrowserRouter>
    )
  }
}

export default App;
