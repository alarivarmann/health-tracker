"""Reusable Streamlit UI controls for configuring analysis options."""

from __future__ import annotations

from typing import Optional

import streamlit as st

from .config import ANTHROPIC_API_KEY
from .analysis import get_available_claude_models


def render_model_controls(
    section_key: str,
    *,
    show_heading: bool = True,
    allow_mode_toggle: bool = True
) -> None:
    """Render mode/model selectors and persist selections in session state.

    Args:
        section_key: Unique suffix for Streamlit widget keys to avoid collisions
                     when controls are rendered in multiple sections.
        show_heading: Whether to display a heading above the controls.
    """

    if show_heading:
        st.markdown("### 🤖 Analysis Engine")

    has_api_key = bool(ANTHROPIC_API_KEY and ANTHROPIC_API_KEY != "your_key_here")

    if allow_mode_toggle:
        mode_options = ["Free (Rule-based)"]
        if has_api_key:
            mode_options.append("Claude AI (Paid)")

        current_mode = st.session_state.config_thresholds.get("mode", "Free")
        current_mode_label = "Claude AI (Paid)" if current_mode == "Claude AI" else "Free (Rule-based)"
        if current_mode_label not in mode_options:
            current_mode_label = mode_options[0]

        selected_mode_label = st.radio(
            "Select analysis mode",
            options=mode_options,
            index=mode_options.index(current_mode_label),
            horizontal=True,
            key=f"mode_selector_{section_key}",
        )

        new_mode = "Claude AI" if selected_mode_label.startswith("Claude") else "Free"
        st.session_state.config_thresholds["mode"] = new_mode
    else:
        # Respect existing session mode but don't render the toggle.
        new_mode = st.session_state.config_thresholds.get("mode", "Free")

    if new_mode == "Claude AI" and has_api_key:
        models = get_available_claude_models()
        model_options = {model["name"]: model["id"] for model in models}

        current_model_id = st.session_state.config_thresholds.get("claude_model", models[0]["id"])
        current_model_name: Optional[str] = next(
            (name for name, model_id in model_options.items() if model_id == current_model_id),
            models[0]["name"],
        )

        selected_model_name = st.selectbox(
            "Claude model",
            options=list(model_options.keys()),
            index=list(model_options.keys()).index(current_model_name),
            key=f"claude_model_selector_{section_key}",
            help="Switch between Claude variants to compare narrative quality and cost.",
        )

        st.session_state.config_thresholds["claude_model"] = model_options[selected_model_name]
    elif new_mode == "Free":
        if allow_mode_toggle:
            st.caption("Using offline rule-based narrative generation (no API calls).")
    else:
        if allow_mode_toggle:
            st.info("Add `ANTHROPIC_API_KEY` to enable Claude AI models.")
