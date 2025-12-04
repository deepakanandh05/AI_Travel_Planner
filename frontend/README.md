# AI Travel Planner Frontend

Modern React frontend for the AI Travel Planner agent.

## Features

- 🎨 Modern dark theme UI inspired by Claude.ai
- 💬 Real-time chat interface
- 📝 Markdown rendering for formatted responses
- 🎯 Example prompts to get started
- ⚡ Fast and responsive

## Tech Stack

- React 18 with Vite
- TailwindCSS for styling
- react-markdown with syntax highlighting
- lucide-react icons

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:3000`

## Backend Integration

The frontend expects the backend API to be running on `http://localhost:8000`

Start the backend with:
```bash
cd ../backend
python api.py
```

## Build for Production

```bash
npm run build
```

The production files will be in the `dist/` directory.
