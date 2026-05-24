# API and Service Boundaries

This project chooses Streamlit, so it does not expose public REST routes. The application still uses clear service boundaries that mirror API endpoints.

## `identify(image)`

Equivalent route: `POST /identify`

Input:

```json
{
  "image": "PIL image object",
  "image_name": "leaf.jpg"
}
```

Output:

```json
{
  "status": "identified",
  "common_name": "Sunflower",
  "scientific_name": "Helianthus annuus",
  "category": "flower",
  "confidence": 0.42,
  "confidence_percent": "42%",
  "summary": "A tall annual with a large composite flower head.",
  "fun_facts": ["The flower head is made of many smaller florets."],
  "toxicity_note": "Do not consume based on AI identification.",
  "origin": "Annual sunflower plant",
  "habitat": "Open fields, gardens, roadsides, and disturbed soil.",
  "regions": ["North America", "Europe", "Asia"],
  "similar_species": ["Black-eyed Susan", "Jerusalem artichoke"],
  "model_used": "openai/clip-vit-base-patch32",
  "safety_disclaimer": "AI identification may be incorrect."
}
```

Low-confidence output sets `status` to `low_confidence` and includes `low_confidence_message` with `Unable to confidently identify.`

## `save_search(image_bytes, image_name, result)`

Equivalent route: `POST /history`

Stores the result JSON, image hash, display names, category, confidence, status, and model name.

## `fetch_recent_searches(limit)`

Equivalent route: `GET /history?limit=25`

Returns recent search records in reverse chronological order.

## `clear_history()`

Equivalent route: `DELETE /history`

Deletes all local search history rows.

