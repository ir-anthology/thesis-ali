# SPARQL Chat

A conversational chat interface for generating and executing SPARQL queries against DBLP publications using natural language.

## Features

- **Natural Language to SPARQL**: Ask questions in plain English and get SPARQL queries
- **Execute Queries**: Run SPARQL queries directly from the chat
- **Results Display**: View query results in a formatted table
- **Copy to Clipboard**: One-click copy for SPARQL queries
- **Dark Theme**: Modern, eye-friendly dark UI
- **Responsive Design**: Works on desktop and mobile

## Tech Stack

- **Frontend**: SvelteKit with Svelte 5
- **Styling**: Tailwind CSS with custom dark theme
- **State Management**: Svelte 5 runes
- **Backend API**: FastAPI (separate repository)

## Prerequisites

- Node.js 18+ 
- Backend server running at `http://127.0.0.1:8000`

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Open http://localhost:5173 in your browser

4. Ensure the backend server is running at http://127.0.0.1:8000

## API Endpoints

The frontend communicates with these backend endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/chat` | POST | Unified endpoint for natural language and SPARQL queries |

The `/chat` endpoint accepts a message and returns a typed response:
- Natural language input → `{type: "sparql", content: "..."}` 
- SPARQL input → `{type: "table", content: "..."}`

## Project Structure

```
src/
├── routes/
│   ├── +layout.svelte          # Root layout
│   └── +page.svelte            # Main chat page
├── lib/
│   ├── components/
│   │   ├── ChatHeader.svelte   # App header
│   │   ├── ChatInput.svelte    # Message input
│   │   ├── ChatMessage.svelte  # Message bubbles
│   │   ├── SparqlCodeBlock.svelte # SPARQL display
│   │   └── TableResult.svelte  # Results table
│   ├── stores/
│   │   └── chat.svelte.js      # Chat state
│   └── api/
│       └── client.ts           # API client
└── app.css                     # Global styles
```

## Usage

1. Type a natural language request in the input field
2. Press Enter or click Send
3. View the generated SPARQL query
4. Click **Execute** to run the query
5. View the results in the table

### Example Queries

- "List all publications from 2023"
- "Find authors who published in SIGMOD"
- "Show me publications with their venues and years"

## Scripts

```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run preview  # Preview production build
npm run check    # Run type checking
```

## License

MIT
