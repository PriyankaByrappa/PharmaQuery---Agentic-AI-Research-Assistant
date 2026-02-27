# PharmaQuery - Frontend

React + TypeScript frontend for the PharmaQuery drug repurposing intelligence platform.

## Tech Stack

- **Vite** - Build tool and dev server
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **shadcn/ui** - UI components
- **React Router** - Navigation
- **TanStack Query** - Data fetching

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:8080`

## Build

Build for production:
```bash
npm run build
```

Preview production build:
```bash
npm run preview
```

## Project Structure

```
src/
├── components/     # Reusable UI components
│   ├── dashboard/  # Dashboard-specific components
│   ├── landing/    # Landing page components
│   └── ui/         # shadcn/ui components
├── pages/          # Page components
├── lib/            # Utilities and API client
└── hooks/          # Custom React hooks
```

## Environment Variables

Create a `.env` file in the `client` directory:

```
VITE_API_URL=http://localhost:8000
```
