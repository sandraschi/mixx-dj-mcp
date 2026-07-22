import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Decks from "./pages/Decks";
import Library from "./pages/Library";
import Effects from "./pages/Effects";
import Tools from "./pages/Tools";
import Chat from "./pages/Chat";
import Settings from "./pages/Settings";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/decks" element={<Decks />} />
        <Route path="/library" element={<Library />} />
        <Route path="/effects" element={<Effects />} />
        <Route path="/tools" element={<Tools />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/settings" element={<Settings />} />
      </Route>
    </Routes>
  );
}
