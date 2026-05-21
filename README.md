# Polymarket Energy Relevance Filter

Automated pipeline that fetches Polymarket prediction market questions, scores them for relevance to **European gas and power markets** using Gemini, and stores results for further analysis.

## How it works

1. Fetch all active Polymarket questions
2. Remove obvious non-energy topics via keyword blacklist
3. Score remaining questions 0–10 via Gemini (prompted as Senior Energy Markets Analyst)
4. Append relevant results with score, reasoning, and impact type to a JSONL history file

Runs twice a day via GitHub Actions.

## Stack

Python · Polymarket Gamma API · Google Gemini API · GitHub Actions

## Setup

```bash
pip install google-genai requests
export GEMINI_API_KEY=your_key_here
```

## Status

Pipeline running. Dashboard in development.
