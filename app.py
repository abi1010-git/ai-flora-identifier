from __future__ import annotations

import sys
import logging
from html import escape
from io import BytesIO
from pathlib import Path

import streamlit as st
from PIL import Image, UnidentifiedImageError

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from floravision.config import get_settings
from floravision.database import clear_history, fetch_recent_searches, init_db, save_search
from floravision.identifier import FloraIdentifier
from floravision.safety import REQUIRED_DISCLAIMER
from floravision.styles import page_css


settings = get_settings()
logger = logging.getLogger(__name__)
MAX_UPLOAD_BYTES = 12 * 1024 * 1024
MIN_IMAGE_SIDE = 64

CAPABILITY_ITEMS = [
    "Leaves",
    "Flowers",
    "Trees",
    "Mushrooms",
    "Fungi",
    "Moss",
    "Grass",
    "Shrubs",
    "Vines",
    "Fruits",
    "Seeds",
    "Cacti",
    "Succulents",
    "Aquatic plants",
]

NOT_ALLOWED_ITEMS = [
    "people",
    "animals",
    "vehicles",
    "buildings",
    "screenshots",
    "prepared food",
    "household objects",
]


def h(value: object) -> str:
    return escape(str(value), quote=True)


@st.cache_resource
def get_identifier() -> FloraIdentifier:
    return FloraIdentifier(settings=settings)


@st.cache_resource
def prepare_database() -> None:
    init_db(settings.db_path)


def main() -> None:
    st.set_page_config(
        page_title=settings.app_name,
        page_icon="FV",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    prepare_database()

    with st.sidebar:
        st.title("FloraVision AI")
        page = st.radio("Navigation", ["Identify", "History", "Model"], label_visibility="collapsed")
        theme = st.segmented_control("Theme", ["Light", "Dark"], default="Light")
        st.caption(REQUIRED_DISCLAIMER)

    st.markdown(page_css(theme or "Light"), unsafe_allow_html=True)

    if page == "Identify":
        identify_page()
    elif page == "History":
        history_page()
    else:
        model_page()


def identify_page() -> None:
    st.markdown(
        """
        <div class="fv-header">
          <h1 class="fv-title">FloraVision AI</h1>
          <p class="fv-subtitle">Upload a flora photo to identify the closest catalog match with an open-source vision model. Only flora images are allowed.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_capabilities()

    upload_col, result_col = st.columns([0.92, 1.08], gap="large")

    with upload_col:
        render_upload_rules()
        uploaded = st.file_uploader(
            "Drag and drop image",
            type=["jpg", "jpeg", "png", "webp"],
            accept_multiple_files=False,
            help="Drag and drop an image here, or choose a file.",
        )

        image = None
        image_bytes = None
        upload_error = None
        if uploaded is not None:
            image_bytes = uploaded.getvalue()
            upload_error = validate_upload(image_bytes, uploaded.name)
            if upload_error is None:
                try:
                    image = Image.open(BytesIO(image_bytes)).convert("RGB")
                    if min(image.size) < MIN_IMAGE_SIDE:
                        upload_error = "Please upload a larger image. The shortest side must be at least 64 pixels."
                        image = None
                except (UnidentifiedImageError, OSError, ValueError):
                    upload_error = "That file could not be read as an image. Please upload a JPG, PNG, or WebP photo."

        if upload_error:
            st.session_state["last_result"] = ui_error_result("Upload blocked", upload_error)
            render_inline_error(upload_error)

        if image is not None:
            st.image(image, caption=uploaded.name, use_container_width=True)
            if st.button("Identify flora", type="primary", use_container_width=True):
                with st.spinner("Analyzing flora image..."):
                    try:
                        result = get_identifier().identify(image)
                        if result["status"] == "rejected_non_flora":
                            st.session_state["last_result"] = result
                        else:
                            save_search(settings.db_path, image_bytes or b"", uploaded.name, result)
                            st.session_state["last_result"] = result
                    except Exception:
                        logger.exception("Flora identification failed")
                        st.session_state["last_result"] = ui_error_result(
                            "Identification failed",
                            "Something went wrong while analyzing the image. Please try a different clear flora photo.",
                        )
        else:
            st.markdown(
                """
                <div class="fv-card fv-card-accent">
                  <div class="fv-label">Ready</div>
                  <div class="fv-value">Leaves, flowers, mushrooms, moss, fruits, seeds, trees, cacti, succulents, and aquatic plants.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with result_col:
        result = st.session_state.get("last_result")
        if result:
            render_result(result)
        else:
            render_empty_result()


def validate_upload(image_bytes: bytes, image_name: str) -> str | None:
    if not image_bytes:
        return "The upload was empty. Please choose a JPG, PNG, or WebP image."
    if len(image_bytes) > MAX_UPLOAD_BYTES:
        return "Please upload an image under 12MB so the app can analyze it reliably."
    suffix = Path(image_name).suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
        return "Unsupported file type. Please upload a JPG, PNG, or WebP image."
    return None


def ui_error_result(title: str, message: str) -> dict:
    return {
        "status": "error",
        "title": title,
        "message": message,
        "safety_disclaimer": REQUIRED_DISCLAIMER,
    }


def render_capabilities() -> None:
    pills = "".join(f'<span class="fv-capability">{h(item)}</span>' for item in CAPABILITY_ITEMS)
    not_allowed = ", ".join(NOT_ALLOWED_ITEMS)
    st.markdown(
        f"""
        <div class="fv-capability-panel">
          <div>
            <div class="fv-label">What the AI can identify</div>
            <div class="fv-capability-grid">{pills}</div>
          </div>
          <div class="fv-rule-card">
            <div class="fv-label">Upload rule</div>
            <p>Use clear flora photos only. Non-flora images are not allowed: {h(not_allowed)}.</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_upload_rules() -> None:
    st.markdown(
        """
        <div class="fv-upload-hint">
          <div class="fv-label">Best results</div>
          <p>Center the plant, fungus, leaf, flower, fruit, seed, or moss in the frame. Avoid people, pets, documents, and unrelated objects.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_inline_error(message: str) -> None:
    st.markdown(
        f'<div class="fv-error-card"><strong>Upload error</strong><br>{h(message)}</div>',
        unsafe_allow_html=True,
    )


def render_result(result: dict) -> None:
    if result["status"] == "error":
        render_error_result(result)
        return

    if result["status"] == "rejected_non_flora":
        render_rejection_result(result)
        return

    if result["status"] == "low_confidence":
        st.markdown(
            f'<div class="fv-warning">{h(result["low_confidence_message"])}</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div class="fv-grid">
          <div class="fv-metric">
            <div class="fv-label">Common name</div>
            <div class="fv-value">{h(result["common_name"])}</div>
          </div>
          <div class="fv-metric">
            <div class="fv-label">Scientific name</div>
            <div class="fv-value fv-scientific">{h(result["scientific_name"])}</div>
          </div>
          <div class="fv-metric">
            <div class="fv-label">Confidence</div>
            <div class="fv-value">{h(result["confidence_percent"])}</div>
          </div>
          <div class="fv-metric">
            <div class="fv-label">Category</div>
            <div class="fv-value">{h(result["category"].title())}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="fv-card">
          <div class="fv-label">Summary</div>
          <p>{h(result["summary"])}</p>
        </div>
        <div class="fv-warning">{h(result["safety_disclaimer"])} {h(result["consumption_warning"])}</div>
        <div class="fv-card">
          <div class="fv-label">Poisonous or toxic caution</div>
          <p>{h(result["toxicity_note"])}</p>
        </div>
        <div class="fv-card">
          <div class="fv-label">Plant or tree source</div>
          <p>{h(result["origin"])}</p>
        </div>
        <div class="fv-card">
          <div class="fv-label">Habitat</div>
          <p>{h(result["habitat"])}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_pills("Common regions", result["regions"])
    render_pills("Similar-looking species", result["similar_species"])
    render_pills("Fun facts", result["fun_facts"])

    st.markdown(
        f"""
        <div class="fv-note">
          <strong>Model:</strong> {h(result["model_used"])}<br>
          {h(result["model_note"])}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_rejection_result(result: dict) -> None:
    st.markdown(
        f"""
        <div class="fv-error-card">
          <div class="fv-label">Image not allowed</div>
          <div class="fv-value">Non-flora upload rejected</div>
          <p>{h(result["rejection_message"])}</p>
        </div>
        <div class="fv-grid">
          <div class="fv-metric">
            <div class="fv-label">Flora likelihood</div>
            <div class="fv-value">{h(result["confidence_percent"])}</div>
          </div>
          <div class="fv-metric">
            <div class="fv-label">Validation</div>
            <div class="fv-value">{h(result["validation_method"].replace("-", " ").title())}</div>
          </div>
        </div>
        <div class="fv-note">{h(result["safety_disclaimer"])}</div>
        """,
        unsafe_allow_html=True,
    )
    render_pills("Try uploading", result["fun_facts"])


def render_error_result(result: dict) -> None:
    st.markdown(
        f"""
        <div class="fv-error-card">
          <div class="fv-label">{h(result["title"])}</div>
          <div class="fv-value">Could not analyze image</div>
          <p>{h(result["message"])}</p>
        </div>
        <div class="fv-note">{h(result["safety_disclaimer"])}</div>
        """,
        unsafe_allow_html=True,
    )


def render_pills(label: str, items: list[str]) -> None:
    pills = "".join(f'<span class="fv-pill">{h(item)}</span>' for item in items)
    st.markdown(
        f"""
        <div class="fv-card">
          <div class="fv-label">{h(label)}</div>
          <div class="fv-pill-row">{pills}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_result() -> None:
    st.markdown(
        """
        <div class="fv-card fv-card-accent">
          <div class="fv-label">Result</div>
          <div class="fv-value">Awaiting upload</div>
        </div>
        <div class="fv-note">AI identification may be incorrect.</div>
        """,
        unsafe_allow_html=True,
    )


def history_page() -> None:
    st.markdown(
        """
        <div class="fv-header">
          <h1 class="fv-title">Previous Searches</h1>
          <p class="fv-subtitle">Recent local identifications stored in SQLite.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    rows = fetch_recent_searches(settings.db_path, limit=30)
    clear_col, _ = st.columns([0.25, 0.75])
    with clear_col:
        if rows and st.button("Clear history", use_container_width=True):
            clear_history(settings.db_path)
            st.rerun()

    if not rows:
        st.info("No saved searches yet.")
        return

    st.markdown('<div class="fv-history">', unsafe_allow_html=True)
    for row in rows:
        result = row["result"]
        st.markdown(
            f"""
            <div class="fv-card">
              <div class="fv-label">{h(row["created_at"])}</div>
              <div class="fv-value">{h(row["common_name"])}</div>
              <p class="fv-scientific">{h(row["scientific_name"])}</p>
              <p>{h(row["category"].title())} - {h(result["confidence_percent"])} - {h(row["status"].replace("_", " "))}</p>
              <p>{h(row["image_name"])}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def model_page() -> None:
    st.markdown(
        f"""
        <div class="fv-header">
          <h1 class="fv-title">Model</h1>
          <p class="fv-subtitle">Primary open-source AI: {h(settings.model_id)}</p>
        </div>
        <div class="fv-card">
          <div class="fv-label">How identification works</div>
          <p>CLIP compares the uploaded image with text prompts generated from the flora catalog. The highest-scoring prompt becomes the closest match.</p>
        </div>
        <div class="fv-card">
          <div class="fv-label">Confidence threshold</div>
          <p>{h(f"{settings.confidence_threshold:.2f}")}</p>
        </div>
        <div class="fv-warning">{h(REQUIRED_DISCLAIMER)}</div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
