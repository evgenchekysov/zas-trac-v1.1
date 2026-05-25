import { BrowserRouter, Routes, Route } from "react-router-dom";
import Landing from "./pages/Landing";
import Dispatcher from "./pages/Dispatcher";
import Login from "./pages/Login";
import CreateTicket from "./pages/CreateTicket";


export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/dispatcher" element={<Dispatcher />} />
        <Route path="/login" element={<Login />} />
        <Route path="/create" element={<CreateTicket />} />
      </Routes>
    </BrowserRouter>
  );
}