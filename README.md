# AI Travel Planner 🌍✈️

An intelligent AI-powered travel planning assistant built with React, FastAPI, and LangGraph.

## Features

- 🤖 **AI-Powered Planning**: Uses LLM agents to create personalized travel itineraries
- 🌦️ **Real-time Weather**: Check current weather conditions for destinations
- 🏨 **Smart Recommendations**: Find hotels, restaurants, and attractions
- 💬 **Conversational Interface**: Natural language interaction with streaming responses
- 🧠 **Transparent Reasoning**: See the AI's thinking process in real-time
- 💾 **Session Memory**: Maintains conversation context

## Tech Stack

### Frontend
- **React** with Vite
- **Tailwind CSS** for styling
- **Lucide React** for icons
- **React Markdown** for formatted responses

### Backend
- **FastAPI** for REST API
- **LangGraph** for AI agent workflow
- **Google Gemini** for LLM inference
- **SQLite** for conversation memory
- **Docker** for deployment

## Local Development

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- Google Gemini API key (get from [Google AI Studio](https://makersuite.google.com/app/apikey))
- Geoapify API key (get from [Geoapify](https://www.geoapify.com/))
- OpenWeatherMap API key (get from [OpenWeatherMap](https://openweathermap.org/api))

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and add your API keys.

5. Run the server:
   ```bash
   uvicorn main:app --reload
   ```
   Backend will run on `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run development server:
   ```bash
   npm run dev
   ```
   Frontend will run on `http://localhost:3000`

4. Open browser and visit `http://localhost:3000`

## Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions on deploying to Render.

### Quick Deploy Summary

**Backend (Docker Web Service)**:
- Root directory: `backend`
- Runtime: Docker
- Environment variables: `GEMINI_API_KEY`, `GEOAPIFY_API_KEY`, `OPEN_WEATHER_API_KEY`, `ALLOWED_ORIGINS`

**Frontend (Static Site)**:
- Root directory: `frontend`
- Build command: `npm install && npm run build`
- Publish directory: `dist`
- Environment variables: `VITE_API_URL`

## Project Structure

```
ai_trip_planner/
├── backend/
│   ├── travel_planner/          # Main Python package
│   │   ├── agent/               # LangGraph agent workflow
│   │   ├── tools/               # Agent tools (weather, search, etc.)
│   │   ├── core/                # Core utilities and validators
│   │   └── utils/               # Logging and session management
│   ├── main.py                  # FastAPI application
│   ├── api.py                   # API endpoints
│   ├── Dockerfile               # Docker configuration
│   ├── requirements.txt         # Python dependencies
│   └── .env.example             # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── App.jsx              # Main application
│   │   └── index.css            # Tailwind styles
│   ├── vite.config.js           # Vite configuration
│   ├── package.json             # Node dependencies
│   └── .env.example             # Frontend env template
└── DEPLOYMENT.md                # Deployment guide
```

## Environment Variables

### Backend
- `GEMINI_API_KEY`: Required - Your Google Gemini API key
- `GEOAPIFY_API_KEY`: Required - Your Geoapify API key for location services
- `OPEN_WEATHER_API_KEY`: Required - Your OpenWeatherMap API key for weather data
- `OPENAI_API_KEY`: Optional - Only if using OpenAI models
- `ALLOWED_ORIGINS`: CORS origins (comma-separated URLs)

### Frontend
- `VITE_API_URL`: Backend API URL (empty for local dev with proxy)

## API Endpoints

- `GET /api/health` - Health check endpoint
- `POST /api/chat` - Standard chat endpoint (returns complete response)
- `POST /api/chat/stream` - Streaming chat endpoint (SSE with thinking steps)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Open an issue on GitHub
- Check [DEPLOYMENT.md](./DEPLOYMENT.md) for deployment troubleshooting
