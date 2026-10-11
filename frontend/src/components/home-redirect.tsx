import { Navigate } from "react-router-dom";

import { useSession } from "@/hooks/use-session";

export function HomeRedirect() {
  const session = useSession();

  if (session === undefined) {
    return (
      <main className="p-8 text-sm text-muted-foreground">Loading…</main>
    );
  }

  return <Navigate to={session ? "/chat" : "/sign-in"} replace />;
}
