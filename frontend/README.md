# Jarvis Lead Finder Frontend

This is the frontend application for the Jarvis Lead Finder module, which helps digital agencies find local businesses with weak or non-existent online presence.

## Features

- Simple, clean UI built with Next.js and Tailwind CSS
- Form to enter search queries like "plumbers in Manchester"
- Real-time results display in a sortable table
- Filter for high-priority leads (businesses without websites)
- Responsive design that works on desktop and mobile

## Technology Stack

- **Framework**: Next.js (React)
- **Styling**: Tailwind CSS
- **Data Fetching**: Axios and React Query
- **State Management**: React Hooks

## Getting Started

1. Install dependencies:
```bash
npm install
# or
yarn install
```

2. Run the development server:
```bash
npm run dev
# or
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the application.

## Environment Variables

The following environment variables can be set in a `.env.local` file:

- `API_URL`: URL of the backend API (defaults to `http://localhost:8000`)

Example `.env.local` file:
```
API_URL=http://localhost:8000
```

## Deployment

This frontend is designed to be deployed to Vercel:

1. Push your code to a GitHub repository
2. Connect the repository to Vercel
3. Set the environment variables in the Vercel dashboard
4. Deploy!

## Backend Connection

This frontend expects a backend API running at the URL specified in the `API_URL` environment variable. The backend should provide:

- `POST /scrape-leads` endpoint to initiate scraping
- `GET /leads` endpoint to retrieve stored leads

See the backend README for more details on setting up the API.