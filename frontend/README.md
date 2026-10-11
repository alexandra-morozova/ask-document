# Frontend

Vite + React + TypeScript SPA for Document Copilot. `pnpm` only. Env is read only through `src/lib/env.ts`. Do not read `import.meta.env` in components.

This is a browser SPA. Do not add Next.js, SSR, server components, or frontend route handlers.

## Prerequisites

- Node.js 22+
- [pnpm](https://pnpm.io) via Corepack (`corepack pnpm` if `pnpm` is not on PATH)
- A `frontend/.env` file with the required variables below (copy from `.env.example`)
- Hosted Supabase project (anon / publishable key only)

From `frontend/`:

```bash
corepack pnpm install
```

`.npmrc` rejects packages published less than 7 days ago (`minimum-release-age=10080`).


## Commands

Run all of these from `frontend/`. Use `corepack pnpm` if `pnpm` is not on PATH.

```bash
corepack pnpm install
```

Install dependencies. Lockfile is `pnpm-lock.yaml`.

```bash
corepack pnpm dev
```

Dev server at `http://localhost:5173`.

| Route | Page |
| --- | --- |
| `/` | Redirects to `/sign-in` |
| `/sign-in` | Email/password via Supabase Auth |
| `/chat` | Placeholder chat (requires a session) |

```bash
corepack pnpm build
corepack pnpm preview
```

Production build and local preview. `build` also typechecks (`tsc -b`).

```bash
corepack pnpm lint
corepack pnpm exec tsc -b --pretty false
```

Oxlint and TypeScript. There is no frontend test runner.

## UI primitives

Add shadcn/ui components with:

```bash
corepack pnpm dlx shadcn@latest add <name>
```

The shadcn CLI calls `pnpm` directly. If that command is missing from PATH, enable Corepack shims (`corepack enable`) or invoke `pnpm` through Corepack.

## Auth (invite-only)

The brief asks for Driftwood email login but does not name a domain. There is no public sign-up in the app.

Until a domain is confirmed:

1. In the Supabase dashboard, disable public sign-up (Authentication → Providers → Email → confirm "Confirm email" / turn off "Enable new user signups" as appropriate).
2. Invite analysts from Authentication → Users → Invite (or Add user). Start with the 5-analyst pilot, then the rest of the firm (~40 analysts plus a few partners).
3. Each invitee sets a password from the email and signs in at `/sign-in`.

When Driftwood confirms the company email domain, set both `VITE_ALLOWED_EMAIL_DOMAIN` in `frontend/.env` and `ALLOWED_EMAIL_DOMAIN` in `backend/.env` (for example `driftwood.com`). Sign-in rejects other domains in the browser; FastAPI rejects them on every authenticated request.
