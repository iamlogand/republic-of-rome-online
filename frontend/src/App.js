import { Component } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home.js";
import JoinGame from "./pages/JoinGame.js";
import SignInPage from "./pages/SignInPage.js";
import SignOutPage from "./pages/SignOutPage.js";
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
        <div className="content">
          <Routes>
            <Route index element={<div><Home /></div>} />
            <Route path="join-game" element={this.state.username === ""
              ? <Navigate to='/auth/sign-in' />
              : <JoinGame
                accessToken={this.state.accessToken}
                refreshToken={this.state.refreshToken}
                setAuthData={this.setAuthData} />} />
            <Route path="auth">
              <Route path="sign-in" element={this.state.username === ""
                ? <SignInPage setAuthData={this.setAuthData} />
                : <Navigate to='/' />} />
              <Route path="sign-out" element={this.state.username === ""
                ? <Navigate to='/' />
                : <SignOutPage setAuthData={this.setAuthData} />} />
            </Route>
          </Routes>
        </div>
      </BrowserRouter>
    )
  }
}

export default App;
