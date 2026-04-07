# Coconut Research Assistant

A full-stack research agent application for planning, executing, and synthesizing multi-step web research.

This project is built as a portfolio-grade evolution of the original deep research example. It focuses on agent orchestration, streaming UX, structured task execution, and report generation, while being refactored into a cleaner software architecture suitable for continued extension.

## What It Does

- breaks a research topic into actionable tasks
- runs tool-using web research for each task
- streams progress updates to the frontend in real time
- tracks task status, sources, notes, and tool calls
- synthesizes a final Markdown report from intermediate results

## Why This Project

Most agent demos stop at a single prompt-response loop. This project is designed to look more like a real agent application:

- a backend orchestration layer instead of a single script
- structured task planning and execution
- observable intermediate state
- a frontend that shows live progress rather than only final output
- room to grow into memory, session persistence, and framework abstraction

## Architecture

### Backend

The backend is a FastAPI application organized under `backend/src/app`:

```text
backend/src/app/
├── agents/     # agent orchestration
├── api/        # FastAPI app, routes, request/response schemas
├── core/       # config, prompts, shared utilities
├── models/     # workflow state and domain models
└── services/   # planning, search, summarization, reporting, tool events
```

Current backend responsibilities:

- `api`: HTTP entrypoints and SSE streaming endpoints
- `agents`: top-level research workflow coordination
- `services`: planning, search dispatch, summarization, reporting, note/tool event handling
- `core`: configuration loading and prompt definitions

### Frontend

The frontend is a Vue 3 + Vite application. It has been split from a monolithic `App.vue` into smaller UI components:

```text
frontend/src/
├── components/
│   ├── ResearchInputPanel.vue
│   ├── ResearchSidebar.vue
│   ├── ProgressTimeline.vue
│   ├── TaskList.vue
│   ├── TaskDetail.vue
│   └── ReportPanel.vue
├── services/
├── types/
└── App.vue
```

Current frontend responsibilities:

- submit research topics and optional search backend selection
- subscribe to streaming backend events
- display task timeline, task-level details, tool calls, and final report

## Tech Stack

- Backend: Python, FastAPI, Pydantic, Loguru
- Frontend: Vue 3, TypeScript, Vite
- Agent framework: `hello-agents`
- Search backends: configurable via environment and HelloAgents tooling

## Current Status

Completed:

- project extracted into its own repository structure
- backend refactored into an `app/...` layout
- frontend split into reusable components
- backend startup verified locally
- frontend production build verified locally

In progress:

- tightening dependency management
- improving README/project presentation
- preparing framework integration boundaries for future abstraction

Planned:

- isolate `hello-agents` usage behind a dedicated integration layer
- add session/state persistence
- add tests for backend workflow pieces
- improve deployment and demo documentation

## Local Development

### Backend

```bash
cd backend
conda create -n coconut-research python=3.10 -y
conda activate coconut-research
pip install --upgrade pip
pip install -e .
cp .env.example .env
python src/main.py
```

Notes:

- This project currently depends on `hello-agents`.
- If startup fails because of a missing dependency in the chain, install the missing package in the same environment and retry.
- To enable stronger web research results, configure at least one search provider such as `TAVILY_API_KEY` in `backend/.env`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Production build:

```bash
npm run build
```

## API Surface

Main backend endpoints:

- `GET /healthz`
- `POST /research`
- `POST /research/stream`

The streaming endpoint is used by the frontend to render incremental workflow progress.

## Repository Goal

The long-term goal of this repository is not only to ship a working research agent UI, but also to use it as a vehicle for learning:

- how to structure agent applications beyond toy demos
- how to integrate and eventually abstract an agent framework
- how to expose intermediate agent state to users in a usable way
- how to grow an agent project into a cleaner, more maintainable system
