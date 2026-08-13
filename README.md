# FloraVision AI

FloraVision AI is a Streamlit website that lets a user upload a flora photo, preview it, identify the likely species, and save previous searches in SQLite.

Live app: https://floravisionai.streamlit.app/

## Chosen Stack

- Frontend and web app: Streamlit
- Language: Python
- Database: SQLite
- AI: Open-source OpenAI CLIP model, `openai/clip-vit-base-patch32`, through Hugging Face Transformers

Whisper is an open-source OpenAI model, but it is for speech recognition. This project uses CLIP instead because the task is image identification.

## Folder Structure

```text
.
├── app.py
├── data/
│   └── flora_catalog.json
├── docs/
│   ├── API.md
│   ├── ARCHITECTURE.md
│   └── IMPLEMENTATION_PLAN.md
├── src/
│   └── floravision/
│       ├── __init__.py
│       ├── catalog.py
│       ├── config.py
│       ├── database.py
│       ├── identifier.py
│       ├── safety.py
│       └── styles.py
├── tests/
│   ├── test_catalog.py
│   ├── test_database.py
│   └── test_safety.py
├── .env.example
├── .gitignore
├── requirements.txt
└── .streamlit/
    └── config.toml
```

## Architecture

Streamlit owns the UI, navigation, upload flow, loading states, error states, light/dark mode switch, and result rendering. The code under `src/floravision` holds the reusable application logic:

- `config.py` reads environment variables.
- `catalog.py` loads the starter flora species catalog.
- `identifier.py` runs CLIP zero-shot matching against the catalog. If CLIP dependencies are missing, it uses a clearly labeled local color/texture fallback so the interface remains usable during setup.
- `database.py` creates and reads SQLite search history.
- `safety.py` centralizes required safety copy.
- `styles.py` keeps the Streamlit CSS separate from app logic.

The CLIP model scores the uploaded image against catalog prompts such as common name, scientific name, category, and visual terms. The highest-scoring catalog item becomes the best match, and nearby matches become similar-looking species.

## Database Schema

```sql
CREATE TABLE IF NOT EXISTS searches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    image_name TEXT NOT NULL,
    image_sha256 TEXT NOT NULL,
    common_name TEXT NOT NULL,
    scientific_name TEXT NOT NULL,
    category TEXT NOT NULL,
    confidence REAL NOT NULL,
    status TEXT NOT NULL,
    model_used TEXT NOT NULL,
    result_json TEXT NOT NULL
);
```

## API Endpoints

Because this version uses Streamlit, there are no public REST endpoints. The app is organized around equivalent internal service boundaries:

- `identify(image)` analyzes an uploaded image and returns a structured result.
- `save_search(image_bytes, image_name, result)` stores a previous search.
- `fetch_recent_searches(limit)` returns search history.
- `clear_history()` removes stored history.

See `docs/API.md` for request/response shapes.

## Step-by-Step Implementation Plan

1. Build a clean Streamlit shell with navigation, upload, preview, theme controls, loading states, and error states.
2. Add a curated starter flora catalog that covers leaves, plants, flowers, trees, mushrooms, fungi, moss, grass, shrubs, bushes, vines, fruits, seeds, cacti, succulents, and aquatic plants.
3. Implement CLIP zero-shot image matching with confidence scoring and a low-confidence rule.
4. Add safety text so the app never claims a plant or mushroom is definitely safe and always displays “AI identification may be incorrect.”
5. Persist previous searches in SQLite.
6. Add unit tests for catalog loading, safety copy, and database behavior.
7. Document setup, run, test, and future improvement steps.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The first real CLIP identification can take time because Transformers downloads the model weights.

## Run

```powershell
streamlit run app.py
```

## Test

```powershell
python -m unittest discover -s tests
```

## Environment Variables

Copy `.env.example` if you want local overrides. No API key is required.

```text
FLORAVISION_DB_PATH=data/floravision.sqlite3
FLORAVISION_MODEL_ID=openai/clip-vit-base-patch32
FLORAVISION_CONFIDENCE_THRESHOLD=0.17
FLORAVISION_FLORA_GATE_THRESHOLD=0.45
```

## Safety Rules

The app always includes:

> AI identification may be incorrect.

If confidence is low, the app says:

> Unable to confidently identify.

It does not guarantee that any plant, mushroom, fruit, seed, or fungus is safe to eat or non-toxic.

The app also blocks likely non-flora uploads. People, animals, vehicles, buildings, screenshots, prepared food, and household objects are not supported inputs.

## Future Improvements

- Expand the flora catalog with regional candidate lists.
- Add GPS or region filters to improve species matching.
- Add a dedicated plant-identification model trained on iNaturalist or PlantCLEF data.
- Store optional thumbnails after adding privacy controls.
- Add user accounts and exportable search logs.
- Add expert review workflow for low-confidence identifications.
