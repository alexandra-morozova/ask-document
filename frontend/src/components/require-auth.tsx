import { type ReactNode } from "react";
import { Navigate } from "react-router-dom";

import { useSession } from "@/hooks/use-session";

export function RequireAuth({ children }: { children: ReactNode }) {
  const session = useSession();

  if (session === undefined) {
    return (
      <main className="p-8 text-sm text-muted-foreground">Loading…</main>
    );
  }

  if (session === null) {
    return <Navigate to="/sign-in" replace />;
  }

  return children;
}
