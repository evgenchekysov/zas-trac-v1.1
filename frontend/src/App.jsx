import { BrowserRouter, Routes, Route } from "react-router-dom";
import Landing from "./pages/Landing";
import Dispatcher from "./pages/Dispatcher";
import Login from "./pages/Login";
import CreateTicket from "./pages/CreateTicket";
import Work from './pages/Work'
import Timeline from "./pages/Timeline";
import Reports from "./pages/Reports";
import Analytics from "./pages/Analytics";
import Settings from "./pages/Settings";
import TicketPage from "./pages/TicketPage";

console.log("✅ NEW BUILD WORK ROUTE");

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/dispatcher" element={<Dispatcher />} />
        <Route path="/login" element={<Login />} />
        <Route path="/create" element={<CreateTicket />} />
        <Route path="/work" element={<Work />} />
        <Route path="/timeline" element={<Timeline />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/tickets/:id" element={<TicketPage />} />
      </Routes>
    </BrowserRouter>
  );
}