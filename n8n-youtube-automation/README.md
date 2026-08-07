# YT Automate - n8n YouTube Automation Dashboard

A React dashboard for managing faceless YouTube automation workflows powered by n8n.

## Quick Start

```bash
npm install
npm run dev
```

## ngrok Setup

This project includes ngrok configuration for exposing local services publicly.

### Configuration

The following are set in `.env`:

```
NGROK_AUTHTOKEN=36cQXTHuoRnyna1ZDgWk2sZnURn_3dtV7ory39KFT93SSQ9GG
WEBHOOK_URL=https://zanyish-gramophonically-kohen.ngrok-free.dev
```

### Commands

```bash
# Start ngrok tunnel for the Vite dev server (port 5173)
npm run ngrok

# Start ngrok tunnel for n8n (port 5678)
npm run ngrok:n8n

# Run dev server + ngrok tunnel together
npm run tunnel
```

### ngrok Config

`ngrok.yml` is included in the project root with reserved domain configuration.

## Available Scripts

| Script | Description |
|--------|-------------|
| `npm run dev` | Start Vite dev server |
| `npm run build` | Production build |
| `npm run preview` | Preview production build |
| `npm run ngrok` | Start ngrok tunnel for dev server |
| `npm run ngrok:n8n` | Start ngrok tunnel for n8n |
| `npm run tunnel` | Run dev + ngrok together |
| `npm run lint` | Run oxlint |

## n8n Integration

The dashboard connects to n8n via REST API. Configure your n8n instance in Settings or via `.env`:

```
VITE_N8N_API_URL=http://localhost:5678
VITE_N8N_API_KEY=your_n8n_api_key
```
