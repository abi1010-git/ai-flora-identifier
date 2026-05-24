# Implementation Plan

## 1. Project Foundation

- Create a beginner-friendly folder structure.
- Add a README with architecture, schema, setup, run, test, and improvement notes.
- Add environment variable support and `.gitignore`.

## 2. UI

- Build a Streamlit upload page with image preview.
- Add navigation for Identify, History, and Model.
- Add light and dark mode styling.
- Add loading indicators and friendly error states.

## 3. AI Identification

- Use OpenAI CLIP through Transformers as the open-source image model.
- Compare each uploaded image against prompts generated from the flora catalog.
- Return common name, scientific name, confidence, category, summary, facts, toxicity caution, habitat, regions, origin, and similar species.
- If dependencies are not installed, use a local fallback and label it clearly.

## 4. Safety

- Always display `AI identification may be incorrect.`
- Display `Unable to confidently identify.` when confidence is below the configured threshold.
- Avoid any claim that a plant or mushroom is definitely safe to eat or guaranteed non-toxic.

## 5. Persistence

- Create the SQLite schema on startup.
- Save each completed search with the image hash and structured result JSON.
- Render recent searches in the History view.

## 6. Verification

- Add unit tests for catalog coverage, safety language, and database operations.
- Run `python -m unittest discover -s tests`.
- Start the Streamlit server and verify the app loads.

