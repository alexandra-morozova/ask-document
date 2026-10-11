import { useNavigate } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { useSession } from "@/hooks/use-session";
import { supabase } from "@/lib/supabase";

export function ChatPage() {
  const session = useSession();
  const navigate = useNavigate();

  async function onSignOut() {
    await supabase.auth.signOut();
    navigate("/sign-in", { replace: true });
  }

  return (
    <main className="flex min-h-svh flex-col gap-4 p-8">
      <div className="flex items-center justify-between gap-4">
        <h1 className="text-2xl font-medium">Chat</h1>
        <Button type="button" variant="outline" onClick={onSignOut}>
          Sign out
        </Button>
      </div>
      {session?.user.email ? (
        <p className="text-sm text-muted-foreground">{session.user.email}</p>
      ) : null}
      <p className="text-muted-foreground">
        Placeholder. Threads and streaming land after the API client is in
        place.
      </p>
    </main>
  );
}
