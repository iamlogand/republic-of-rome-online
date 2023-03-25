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
import { useAuth } from './AuthContext';

const App = () => {
  const [dialog, setDialog] = useState<string>('');
  const { username } = useAuth();

  return (
    <BrowserRouter>
      <div id="page_container">
        <TopBar setDialog={setDialog} />
        <Routes>
          <Route index element={
            <Home />} />

          <Route path="game" element={username === ""
            ? <Navigate to='/' />
            : <GamePage />} />

          <Route path="game-list" element={username === ""
            ? <Navigate to='/' />
            : <GameListPage />} />

          <Route path="game-create" element={username === ""
            ? <Navigate to='/' />
            : <GameCreatePage />} />

          <Route path="account" element={username === ""
            ? <Navigate to='/' />
            : <AccountPage />} />
        </Routes>
        {dialog !== "" &&
          <DialogBackdrop setDialog={setDialog} />
        }
        {dialog === "sign-in" &&
          <SignInDialog setDialog={setDialog} />
        }
        {dialog === "sign-out" &&
          <SignOutDialog setDialog={setDialog} />
        }
      </div>
    </BrowserRouter>
  )
}

export default App;
