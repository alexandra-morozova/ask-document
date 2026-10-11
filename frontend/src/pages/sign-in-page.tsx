import { type FormEvent, useState } from "react";
import { Navigate } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { useSession } from "@/hooks/use-session";
import { isAllowedEmail } from "@/lib/email";
import { env } from "@/lib/env";
import { supabase } from "@/lib/supabase";

export function SignInPage() {
  const session = useSession();
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const email = String(form.get("email") ?? "");
    const password = String(form.get("password") ?? "");

    if (!isAllowedEmail(email, env.allowedEmailDomain)) {
      setError("Use your Driftwood email.");
      return;
    }

    setPending(true);
    setError(null);
    const { error: signInError } = await supabase.auth.signInWithPassword({
      email,
      password,
    });
    setPending(false);

    if (signInError) {
      setError("Could not sign in. Check your email and password.");
    }
  }

  if (session === undefined) {
    return (
      <main className="p-8 text-sm text-muted-foreground">Loading…</main>
    );
  }

  if (session) {
    return <Navigate to="/chat" replace />;
  }

  return (
    <main className="mx-auto flex min-h-svh w-full max-w-sm flex-col justify-center gap-6 p-8">
      <div className="space-y-1">
        <h1 className="text-2xl font-medium">Sign in</h1>
        <p className="text-sm text-muted-foreground">
          Use your Driftwood email.
        </p>
      </div>
      <form className="flex flex-col gap-4" onSubmit={onSubmit}>
        <label className="flex flex-col gap-1.5 text-sm">
          Email
          <input
            className="h-8 rounded-lg border border-input bg-background px-2.5 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
            name="email"
            type="email"
            autoComplete="email"
            required
          />
        </label>
        <label className="flex flex-col gap-1.5 text-sm">
          Password
          <input
            className="h-8 rounded-lg border border-input bg-background px-2.5 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
            name="password"
            type="password"
            autoComplete="current-password"
            required
          />
        </label>
        {error ? <p className="text-sm text-destructive">{error}</p> : null}
        <Button type="submit" disabled={pending}>
          {pending ? "Signing in…" : "Sign in"}
        </Button>
      </form>
    </main>
  );
}
