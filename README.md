# Coconut Research Assistant

A research-oriented agent application built on top of HelloAgents.

This repository is initialized from the `chapter14` deep research example and will be evolved into a standalone portfolio project with:

- task planning and decomposition
- tool-using web research
- streaming execution updates
- task-level notes and traceability
- final report synthesis

## Current Structure

```text
coconut-research-assistant/
├── backend/
└── frontend/
```


## Backend

The backend is a FastAPI service that orchestrates the research workflow.

Quick start:

```bash
cd backend
conda create -n coconut-research python=3.10 -y
conda activate coconut-research
pip install --upgrade pip
pip install -e .
cp .env.example .env
python src/main.py
```

Note:

- This project currently depends on `hello-agents`.
- If `hello-agents` is not available from your Python environment, install it first in the environment you use for this project.
- If startup fails with a missing module from the dependency chain, install the missing package in the same environment and then retry.
- To enable higher-quality web research, configure at least one search provider such as `TAVILY_API_KEY` in `backend/.env`.

## Frontend

The frontend is a Vue 3 + Vite application.

Quick start:

```bash
cd frontend
npm install
npm run dev
```

## Next Refactor Steps

1. Restructure the backend into `app/api`, `app/agents`, `app/services`, and `app/core`.
2. Split the frontend `App.vue` into smaller components.
3. Isolate HelloAgents integration points behind a thin adapter layer.
4. Add session/state persistence and tests.
