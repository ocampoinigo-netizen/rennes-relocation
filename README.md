# Rennes Relocation — Streamlit Mock

A tiny, runnable mock of the relocation app focused on **Rennes**.

## Quick start
```bash
# Create a virtual env (optional)
python -m venv .venv && source .venv/bin/activate   # on Windows: .venv\Scripts\activate

# Install deps
pip install -r requirements.txt

# Run
streamlit run app.py
```

Then open the local URL Streamlit prints (usually http://localhost:8501).

## What’s included
- Landing screen (nationality, destination, arrival status)
- Branching to **Planning** (pre‑departure checklists & guides)
- Branching to **Arrived** → **Lifestyle** (filterable place list) or **Administrative** (step‑by‑step guides)

## Customize data
Edit the CSV files in `data/`:
- `cities.csv`, `nationalities.csv`, `categories.csv`
- `posts.csv` (guides content in Markdown)
- `places.csv` (restaurants, cafes, activities, etc.)
- `checklists.csv`, `checklist_items.csv`

## Notes
- This is a mock for demonstration. No auth, no persistence of checklist state.
- You can export this structure later to Glide, Bubble, or a simple Flask/React app.