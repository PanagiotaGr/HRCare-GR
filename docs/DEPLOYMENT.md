# HRCare-GR Deployment Guide

This guide explains how to run HRCare-GR locally, with Docker, or on a public server.

## 1. Local development

```bash
git clone https://github.com/PanagiotaGr/HRCare-GR.git
cd HRCare-GR
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
PYTHONPATH=. streamlit run app/streamlit_app.py
```

Open:

```text
http://localhost:8501
```

## 2. Docker

```bash
git clone https://github.com/PanagiotaGr/HRCare-GR.git
cd HRCare-GR
cp .env.example .env
docker compose up --build
```

Open:

```text
http://localhost:8501
```

## 3. OpenAI mode

Edit `.env`:

```bash
HRC_LLM_PROVIDER=openai
HRC_LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=your_api_key_here
```

Restart the app:

```bash
docker compose down
docker compose up --build
```

## 4. Public deployment options

Recommended beginner-friendly options:

- Streamlit Community Cloud for fast public demos.
- Render, Railway, Fly.io, or a VPS for Docker-based deployments.
- University server if this is used for thesis/demo purposes.

## 5. Privacy and safety

Do not upload real patient data to a public deployment. Use anonymized or synthetic patient profiles only.

This project is a research simulation and must not be used for real medical decision-making.
