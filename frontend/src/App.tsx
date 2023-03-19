import "./css/color.css";
import "./css/master.css";
import "./css/form.css";
import "./css/dialog.css";
import "./css/table.css";
import "./css/button.css";
import "./css/layout.css";
import "./css/link.css";
import "./css/heading.css";

import { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/HomePage";
import GamePage from "./pages/GamePage";
import GameListPage from "./pages/GameListPage";
import AccountPage from "./pages/AccountPage";
import { Navigate } from "react-router-dom";
import TopBar from "./components/TopBar";
import SignInDialog from "./dialogs/SignInDialog";
import SignOutDialog from "./dialogs/SignOutDialog";
import DialogBackdrop from "./dialogs/DialogBackdrop";
import GameCreatePage from "./pages/GameCreatePage";

interface AuthData {
  accessToken: string,
  refreshToken: string,
  username: string
}

const App = () => {
  const [accessToken, setAccessToken] = useState<string>(localStorage.getItem('accessToken') || '');
  const [refreshToken, setRefreshToken] = useState<string>(localStorage.getItem('refreshToken') || '');
  const [username, setUsername] = useState<string>(localStorage.getItem('username') || '');
  const [dialog, setDialog] = useState<string>('');

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
      <div id="page_container">
        <TopBar username={username} setDialog={setDialog} />
        <Routes>
          <Route index element={
            <Home username={username} />} />

          <Route path="game" element={username === ""
            ? <Navigate to='/' />
            : <GamePage />} />

          <Route path="game-list" element={username === ""
            ? <Navigate to='/' />
            : <GameListPage
              accessToken={accessToken}
              refreshToken={refreshToken}
              setAuthData={setAuthData} />} />

          <Route path="game-create" element={username === ""
            ? <Navigate to='/' />
            : <GameCreatePage
              accessToken={accessToken}
              refreshToken={refreshToken}
              setAuthData={setAuthData} />} />

          <Route path="account" element={username === ""
            ? <Navigate to='/' />
            : <AccountPage
              username={username}
              accessToken={accessToken}
              refreshToken={refreshToken}
              setAuthData={setAuthData} />} />
        </Routes>
        {dialog != "" &&
          <DialogBackdrop setDialog={setDialog} />
        }
        {dialog == "sign-in" &&
          <SignInDialog setAuthData={setAuthData} setDialog={setDialog} />
        }
        {dialog == "sign-out" &&
          <SignOutDialog setAuthData={setAuthData} setDialog={setDialog} />
        }
      </div>
  </BrowserRouter>
  )
}

export default App;
