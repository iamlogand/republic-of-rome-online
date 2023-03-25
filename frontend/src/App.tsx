import "./css/color.css";
import "./css/space.css";
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
import useLocalStorage from "./helpers/useLocalStorage";

const App = () => {
  const [accessToken, setAccessToken] = useLocalStorage<string>('accessToken', '');
  const [refreshToken, setRefreshToken] = useLocalStorage<string>('refreshToken', '');
  const [username, setUsername] = useLocalStorage<string>('username', '');
  const [dialog, setDialog] = useState<string>('');

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
              setAccessToken={setAccessToken}
              setRefreshToken={setRefreshToken}
              setUsername={setUsername} />} />

          <Route path="game-create" element={username === ""
            ? <Navigate to='/' />
            : <GameCreatePage
              accessToken={accessToken}
              refreshToken={refreshToken}
              setAccessToken={setAccessToken}
              setRefreshToken={setRefreshToken}
              setUsername={setUsername} />} />

          <Route path="account" element={username === ""
            ? <Navigate to='/' />
            : <AccountPage
              username={username}
              accessToken={accessToken}
              refreshToken={refreshToken}
              setAccessToken={setAccessToken}
              setRefreshToken={setRefreshToken}
              setUsername={setUsername} />} />
        </Routes>
        {dialog !== "" &&
          <DialogBackdrop setDialog={setDialog} />
        }
        {dialog === "sign-in" &&
          <SignInDialog
            setAccessToken={setAccessToken}
            setRefreshToken={setRefreshToken}
            setUsername={setUsername}
            setDialog={setDialog} />
        }
        {dialog === "sign-out" &&
          <SignOutDialog
            setAccessToken={setAccessToken}
            setRefreshToken={setRefreshToken}
            setUsername={setUsername}
            setDialog={setDialog} />
        }
      </div>
  </BrowserRouter>
  )
}

export default App;
