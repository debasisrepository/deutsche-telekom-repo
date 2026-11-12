# Deutsche Telekom IT Procurement - Frontend

React + TypeScript + Vite web application for the Deutsche Telekom IT Procurement Supplier Selection Workflow.

## Prerequisites

- Node.js 20.19+ or 22.12+
- npm 9+

## Local Development

### Install Dependencies

```bash
npm install
```

### Start Development Server

From the repository root, use the `start.sh` script which starts both backend and frontend together:

```bash
./start.sh
```

Or start the frontend independently (requires backend to be running on port 9000):

```bash
npm run dev
```

The development server runs on http://localhost:5173 by default.

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Testing

### Unit Tests

```bash
npm test
```

### Type Check

```bash
npm run type-check
```

### Lint

```bash
npm run lint
```

### E2E Tests

```bash
npx playwright install chromium
npx playwright test
```

## Project Structure

```
frontend/
├── src/
│   ├── lib/
│   │   ├── api-client.ts       # Centralized API client
│   │   ├── auth-context.tsx    # AuthProvider + useAuth() hook
│   │   └── utils.ts            # Utility functions
│   ├── types/
│   │   ├── auth.ts             # Auth-related interfaces
│   │   └── common.ts           # Common interfaces
│   ├── components/
│   │   ├── auth/
│   │   │   ├── LoginPage.tsx   # Login form
│   │   │   └── RequireAuth.tsx # Route guard
│   │   └── layout/
│   │       ├── Layout.tsx      # Application shell
│   │       ├── Header.tsx      # Header component
│   │       └── Sidebar.tsx     # Navigation sidebar
│   ├── App.tsx                 # Route table
│   ├── main.tsx                # Entry point
│   └── index.css               # Global styles
├── e2e/                        # Playwright E2E tests
├── vite.config.ts              # Vite configuration
├── tailwind.config.js          # Tailwind CSS configuration
├── playwright.config.ts        # Playwright configuration
└── package.json
```

## API Integration

The frontend calls the backend API at `/api/v1/*` via same-origin requests:

- **Local development**: Vite dev server proxies `/api` to `http://localhost:9000`
- **Production**: nginx serves the frontend and proxies `/api` to the backend service

Authentication uses JWT tokens stored in `localStorage` under the key `access_token`.

## Environment Variables

Create a `.env` file (optional, for non-default API URL):

```bash
# VITE_API_URL=/api
# Only set VITE_API_URL when the API lives on a different public origin
```

For local development, leave `VITE_API_URL` unset to use the default same-origin `/api`.

## Default Login Credentials (Development)

- **Admin**: admin@example.com / admin123
- **Reviewer**: reviewer@example.com / reviewer123
- **Manager**: manager@example.com / manager123

These credentials are seeded by the backend for local development only.
