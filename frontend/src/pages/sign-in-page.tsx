import { type FormEvent } from "react";
import { Link } from "react-router-dom";

import { Button } from "@/components/ui/button";

export function SignInPage() {
  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
  }

  return (
    <main className="mx-auto flex min-h-svh w-full max-w-sm flex-col justify-center gap-6 p-8">
      <div className="space-y-1">
        <h1 className="text-2xl font-medium">Sign in</h1>
        <p className="text-sm text-muted-foreground">
          Driftwood email. Auth is wired in the next phase.
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
        <Button type="submit">Sign in</Button>
      </form>
      <p className="text-sm text-muted-foreground">
        <Link className="underline-offset-4 hover:underline" to="/chat">
          Open placeholder chat
        </Link>
      </p>
    </main>
  );
}
