import { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import GamePage from "./pages/GamePage";
import JoinGame from "./pages/GameListPage";
import RegisterPage from "./pages/RegisterPage";
import SignInPage from "./pages/SignInPage";
import SignOutPage from "./pages/SignOutPage";
import AccountPage from "./pages/AccountPage";
import { Navigate } from "react-router-dom";

import "./css/color.css";
import "./css/master.css";
import "./css/form.css";
import "./css/auth.css";
import "./css/table.css";
import "./css/button.css";
import "./css/layout.css";
import "./css/link.css";

interface AuthData {
  accessToken: string,
  refreshToken: string,
  username: string
}

const App = () => {
  const [accessToken, setAccessToken] = useState<string>(localStorage.getItem('accessToken') || '');
  const [refreshToken, setRefreshToken] = useState<string>(localStorage.getItem('refreshToken') || '');
  const [username, setUsername] = useState<string>(localStorage.getItem('username') || '');

  /**
   * Sets any of these auth values: `accessToken`, `refreshToken`, `username`.
   * Values are saved to both the `App` state and local storage
   * @param {Object} data the key-value pairs to set
   */
  const setAuthData = (data: AuthData) => {
    if (data.accessToken === '') {
      setAccessToken('');
      localStorage.setItem('accessToken', '');
    } else if (data.accessToken) {
      setAccessToken(data.accessToken);
      localStorage.setItem('accessToken', data.accessToken);
    }
    if (data.refreshToken === '') {
      setRefreshToken('');
      localStorage.setItem('refreshToken', '');
    } else if (data.refreshToken) {
      setRefreshToken(data.refreshToken);
      localStorage.setItem('refreshToken', data.refreshToken);
    }
    if (data.username === '') {
      setUsername('');
      localStorage.setItem('username', '');
    } else if (data.username) {
      setUsername(data.username);
      localStorage.setItem('username', data.username);
    }
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route index element={
          <Home username={username} />} />

        <Route path="game" element={
          <GamePage username={username} />} />

        <Route path="join-game" element={username === ""
          ? <Navigate to='/auth/sign-in' />
          : <JoinGame
            username={username}
            accessToken={accessToken}
            refreshToken={refreshToken}
            setAuthData={setAuthData} />} />

        {/* `auth` maps to pages relating to user accounts */}
        <Route path="auth">
          <Route path="register" element={username === ""
            ? <RegisterPage
              username={username}
              setAuthData={setAuthData} />
            : <Navigate to='/' />} />

          <Route path="sign-in" element={username === ""
            ? <SignInPage
              username={username}
              setAuthData={setAuthData} />
            : <Navigate to='/' />} />

          <Route path="sign-out" element={username === ""
            ? <Navigate to='/' />
            : <SignOutPage
              username={username}
              setAuthData={setAuthData} />} />

          <Route path="account" element={username === ""
            ? <Navigate to='/' />
            : <AccountPage
              username={username}
              accessToken={accessToken}
              refreshToken={refreshToken}
              setAuthData={setAuthData} />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App;
