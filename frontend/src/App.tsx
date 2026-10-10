import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { ChatPage } from "@/pages/chat-page";
import { SignInPage } from "@/pages/sign-in-page";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/sign-in" element={<SignInPage />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/" element={<Navigate to="/sign-in" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
