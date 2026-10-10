# Frontend

Vite + React + TypeScript SPA for Document Copilot. `pnpm` only. Env is read only through `src/lib/env.ts`. Do not read `import.meta.env` in components.

This is a browser SPA. Do not add Next.js, SSR, server components, or frontend route handlers.

## Prerequisites

- Node.js 22+
- [pnpm](https://pnpm.io) via Corepack (`corepack pnpm` if `pnpm` is not on PATH)
- A `frontend/.env` file with the required variables below
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
| `/sign-in` | Email/password form (submit is a no-op until auth) |
| `/chat` | Placeholder chat |

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
