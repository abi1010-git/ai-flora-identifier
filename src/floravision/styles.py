from __future__ import annotations


def page_css(mode: str) -> str:
    dark = mode.lower() == "dark"
    colors = {
        "bg": "#07100c" if dark else "#f7faf7",
        "sidebar": "#121f18" if dark else "#ffffff",
        "panel": "#13211a" if dark else "#ffffff",
        "panel_alt": "#172b21" if dark else "#eef5f1",
        "upload": "#0d1812" if dark else "#ffffff",
        "text": "#f4fbf6" if dark else "#17211b",
        "muted": "#bdd1c5" if dark else "#627267",
        "border": "#294638" if dark else "#d9e6de",
        "accent": "#4dd7a4" if dark else "#2f8f6b",
        "accent_2": "#f1d075" if dark else "#a6651f",
        "accent_3": "#86d3e4" if dark else "#2e6fa8",
        "danger": "#ff9f9f" if dark else "#a83c3c",
        "shadow": "rgba(77, 215, 164, 0.18)" if dark else "rgba(47, 143, 107, 0.12)",
    }
    return f"""
    <style>
    :root {{
        --fv-bg: {colors["bg"]};
        --fv-sidebar: {colors["sidebar"]};
        --fv-panel: {colors["panel"]};
        --fv-panel-alt: {colors["panel_alt"]};
        --fv-upload: {colors["upload"]};
        --fv-text: {colors["text"]};
        --fv-muted: {colors["muted"]};
        --fv-border: {colors["border"]};
        --fv-accent: {colors["accent"]};
        --fv-accent-2: {colors["accent_2"]};
        --fv-accent-3: {colors["accent_3"]};
        --fv-danger: {colors["danger"]};
        --fv-shadow: {colors["shadow"]};
    }}

    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {{
        background: var(--fv-bg);
        color: var(--fv-text);
    }}

    [data-testid="stHeader"],
    [data-testid="stToolbar"] {{
        background: var(--fv-bg);
        color: var(--fv-text);
    }}

    [data-testid="stDecoration"] {{
        background: var(--fv-accent);
    }}

    .block-container {{
        max-width: 980px;
        padding-top: 4.9rem;
    }}

    section[data-testid="stSidebar"] {{
        background: var(--fv-sidebar);
        border-right: 1px solid var(--fv-border);
    }}

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span {{
        color: var(--fv-text);
    }}

    section[data-testid="stSidebar"] [role="radiogroup"] label p {{
        color: var(--fv-text);
        font-weight: 650;
        opacity: 1;
    }}

    section[data-testid="stSidebar"] [role="radiogroup"] label {{
        min-height: 1.7rem;
        gap: 0.45rem;
    }}

    h1, h2, h3, h4, p, li, label, span, div {{
        letter-spacing: 0;
    }}

    .fv-header {{
        border-bottom: 1px solid var(--fv-border);
        padding: 0.25rem 0 1rem 0;
        margin-bottom: 1rem;
    }}

    .fv-title {{
        color: var(--fv-text);
        font-size: clamp(2rem, 4vw, 3.4rem);
        line-height: 1.05;
        margin: 0;
        font-weight: 820;
        text-shadow: 0 1px 0 var(--fv-accent-2), 0 0 26px var(--fv-shadow);
    }}

    .fv-subtitle {{
        color: var(--fv-muted);
        font-size: 1.05rem;
        max-width: 52rem;
        margin: 0.65rem 0 0 0;
    }}

    .fv-card {{
        background: var(--fv-panel);
        border: 1px solid var(--fv-border);
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.8rem;
    }}

    .fv-capability-panel {{
        display: grid;
        grid-template-columns: minmax(0, 1fr) minmax(230px, 0.54fr);
        gap: 0.85rem;
        align-items: stretch;
        margin: 0 0 1.2rem 0;
    }}

    .fv-capability-panel > div,
    .fv-upload-hint {{
        background: var(--fv-panel);
        border: 1px solid var(--fv-border);
        border-radius: 8px;
        padding: 0.9rem 1rem;
    }}

    .fv-capability-grid {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        margin-top: 0.55rem;
    }}

    .fv-capability {{
        background: var(--fv-panel-alt);
        border: 1px solid var(--fv-border);
        border-radius: 999px;
        color: var(--fv-text);
        display: inline-flex;
        align-items: center;
        min-height: 2rem;
        padding: 0.24rem 0.62rem;
        font-size: 0.9rem;
        font-weight: 680;
    }}

    .fv-rule-card {{
        border-left: 4px solid var(--fv-accent) !important;
    }}

    .fv-rule-card p,
    .fv-upload-hint p {{
        color: var(--fv-muted);
        margin: 0.35rem 0 0 0;
        line-height: 1.45;
    }}

    .fv-card-accent {{
        border-left: 4px solid var(--fv-accent);
    }}

    .fv-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
        gap: 0.75rem;
        margin: 1rem 0;
    }}

    .fv-metric {{
        background: var(--fv-panel-alt);
        border: 1px solid var(--fv-border);
        border-radius: 8px;
        min-height: 96px;
        padding: 0.85rem;
    }}

    .fv-label {{
        color: var(--fv-muted);
        font-size: 0.78rem;
        text-transform: uppercase;
        font-weight: 700;
    }}

    .fv-value {{
        color: var(--fv-text);
        font-size: 1.05rem;
        font-weight: 720;
        overflow-wrap: anywhere;
        margin-top: 0.25rem;
    }}

    .fv-scientific {{
        font-style: italic;
    }}

    .fv-warning {{
        background: color-mix(in srgb, var(--fv-danger) 12%, var(--fv-panel));
        border: 1px solid color-mix(in srgb, var(--fv-danger) 40%, var(--fv-border));
        color: var(--fv-text);
        border-radius: 8px;
        padding: 0.9rem 1rem;
        margin: 0.8rem 0;
    }}

    .fv-error-card {{
        background: color-mix(in srgb, var(--fv-danger) 14%, var(--fv-panel));
        border: 1px solid color-mix(in srgb, var(--fv-danger) 52%, var(--fv-border));
        border-left: 4px solid var(--fv-danger);
        color: var(--fv-text);
        border-radius: 8px;
        padding: 1rem;
        margin: 0.8rem 0;
    }}

    .fv-error-card p {{
        color: var(--fv-muted);
        margin: 0.45rem 0 0 0;
        line-height: 1.48;
    }}

    .fv-note {{
        background: color-mix(in srgb, var(--fv-accent-3) 12%, var(--fv-panel));
        border: 1px solid color-mix(in srgb, var(--fv-accent-3) 35%, var(--fv-border));
        color: var(--fv-text);
        border-radius: 8px;
        padding: 0.9rem 1rem;
        margin: 0.8rem 0;
    }}

    .fv-pill-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        margin-top: 0.4rem;
    }}

    .fv-pill {{
        border: 1px solid var(--fv-border);
        background: var(--fv-panel-alt);
        color: var(--fv-text);
        border-radius: 999px;
        padding: 0.3rem 0.65rem;
        font-size: 0.9rem;
    }}

    .fv-history {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        gap: 0.85rem;
    }}

    .stButton > button {{
        border-radius: 8px;
        min-height: 2.65rem;
        font-weight: 700;
    }}

    [data-testid="stFileUploader"] > label p {{
        color: var(--fv-muted);
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
    }}

    [data-testid="stFileUploaderDropzone"],
    section[data-testid="stFileUploaderDropzone"] {{
        background: var(--fv-upload) !important;
        border: 1.5px dashed var(--fv-accent) !important;
        border-radius: 8px;
        min-height: 104px;
        padding: 1rem;
        transition: background 160ms ease, border-color 160ms ease, box-shadow 160ms ease;
    }}

    [data-testid="stFileUploaderDropzone"]:hover,
    section[data-testid="stFileUploaderDropzone"]:hover {{
        background: var(--fv-panel-alt) !important;
        border-color: var(--fv-accent-2) !important;
        box-shadow: 0 0 0 3px var(--fv-shadow);
    }}

    [data-testid="stFileUploaderDropzone"] button {{
        background: var(--fv-panel);
        border: 1px solid var(--fv-border);
        color: var(--fv-text);
        border-radius: 8px;
        min-height: 2.5rem;
        font-weight: 700;
    }}

    [data-testid="stFileUploaderDropzone"] button:hover {{
        border-color: var(--fv-accent);
        color: var(--fv-text);
    }}

    [data-testid="stFileUploaderDropzoneInstructions"],
    [data-testid="stFileUploaderDropzoneInstructions"] p,
    [data-testid="stFileUploaderDropzoneInstructions"] span,
    [data-testid="stFileUploaderFile"] {{
        color: var(--fv-muted);
    }}

    .stFileUploader section {{
        border-radius: 8px;
        border-color: var(--fv-border);
    }}

    @media (max-width: 780px) {{
        .block-container {{
            padding-top: 2.5rem;
        }}

        .fv-capability-panel {{
            grid-template-columns: 1fr;
        }}
    }}
    </style>
    """
