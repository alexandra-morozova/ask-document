import { BrowserRouter, Route, Routes } from "react-router-dom";

import { HomeRedirect } from "@/components/home-redirect";
import { RequireAuth } from "@/components/require-auth";
import { ChatPage } from "@/pages/chat-page";
import { SignInPage } from "@/pages/sign-in-page";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/sign-in" element={<SignInPage />} />
        <Route
          path="/chat"
          element={
            <RequireAuth>
              <ChatPage />
            </RequireAuth>
          }
        />
        <Route path="/" element={<HomeRedirect />} />
      </Routes>
    </BrowserRouter>
  );
}
