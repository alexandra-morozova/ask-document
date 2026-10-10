import { Link } from "react-router-dom";

export function ChatPage() {
  return (
    <main className="flex min-h-svh flex-col gap-4 p-8">
      <h1 className="text-2xl font-medium">Chat</h1>
      <p className="text-muted-foreground">
        Placeholder. Threads and streaming land after the API client is in
        place.
      </p>
      <Link
        className="text-sm underline-offset-4 hover:underline"
        to="/sign-in"
      >
        Back to sign in
      </Link>
    </main>
  );
}
