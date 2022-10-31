import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home.js";
import JoinGame from "./pages/JoinGame.js";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/find-game" element={<JoinGame />} />
      </Routes>
    </BrowserRouter>
  )
}
