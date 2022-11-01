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

    const savedAccessToken = localStorage.getItem("accessToken") ?? '';
    const savedUsername = localStorage.getItem("username") ?? '';

    this.state = {
      refreshToken: '',
      accessToken: savedAccessToken,
      username: savedUsername
    };
  }

  setAuthData = (name, token) => {
    this.setState({ username: name });
    localStorage.setItem('username', name)

    this.setState({ accessToken: token });
    localStorage.setItem('accessToken', token)
  }

  render() {
    return (
      <BrowserRouter>
        <TopBar username={this.state.username} />
        <div className="content">
          <Routes>
            <Route index element={<div><Home /></div>} />
            <Route path="join-game" element={<JoinGame accessToken={this.state.accessToken} />} />
            <Route path="auth">
              <Route path="sign-in" element={ this.state.username === ""
                ? <SignInPage setAuthData={this.setAuthData} />
                : <Navigate to='/' /> } />
              <Route path="sign-out" element={ this.state.username === ""
                ? <Navigate to='/' />
                : <SignOutPage setAuthData={this.setAuthData} /> } />
            </Route>
          </Routes>
        </div>
      </BrowserRouter>
    )
  }
}

export default App;
