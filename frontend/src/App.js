import { Component } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home.js";
import JoinGame from "./pages/JoinGame.js";
import LoginPage from "./pages/LoginPage.js";

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      refreshToken: null,
      accessToken: null
    };
  }

  setAccessToken = (token) => {
    this.setState({accessToken: token});
  }

  render() {
    return (
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/join-game" element={<JoinGame accessToken={this.state.accessToken} />} />
          <Route path="/login" element={<LoginPage setAccessToken={this.setAccessToken} />} />
        </Routes>
      </BrowserRouter>
    )
  }
}

export default App;
