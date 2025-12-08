"""Authentication helpers for Streamlit apps."""

from __future__ import annotations

import os
from typing import Optional

import streamlit as st

_PASSWORD_STATE_KEY = "app_password_authenticated"
_PASSWORD_INPUT_KEY = "app_password_input"
_PASSWORD_ATTEMPTED_KEY = "app_password_attempted"


def _load_configured_password() -> Optional[str]:
    """Return the configured app password from Streamlit secrets or environment."""
    secret_password: Optional[str] = None

    # Streamlit secrets take precedence when available
    try:
        if "APP_PASSWORD" in st.secrets:
            secret_password = str(st.secrets["APP_PASSWORD"]).strip()
    except Exception:
        # st.secrets may not be configured locally; ignore access errors
        secret_password = None

    env_password = os.getenv("APP_PASSWORD")

    password = secret_password or env_password
    if password:
        password = password.strip()
    return password or None


def require_app_password() -> None:
    """Guard the app behind a password gate, stopping execution until authenticated.

    The password is sourced from Streamlit secrets (preferred) or the `APP_PASSWORD`
    environment variable as a fallback. Session state is used to remember successful
    authentication for the current browser session.
    """

    app_password = _load_configured_password()
    if not app_password:
        st.error(
            "⚠️ App password missing. Set `APP_PASSWORD` in Streamlit secrets or environment before continuing."
        )
        st.stop()

    if _PASSWORD_ATTEMPTED_KEY not in st.session_state:
        st.session_state[_PASSWORD_ATTEMPTED_KEY] = False

    def _password_entered() -> None:
        entered = st.session_state.get(_PASSWORD_INPUT_KEY, "")
        st.session_state[_PASSWORD_ATTEMPTED_KEY] = True
        if entered == app_password:
            st.session_state[_PASSWORD_STATE_KEY] = True
            st.session_state.pop(_PASSWORD_INPUT_KEY, None)
            st.session_state[_PASSWORD_ATTEMPTED_KEY] = False
        else:
            st.session_state[_PASSWORD_STATE_KEY] = False

    if st.session_state.get(_PASSWORD_STATE_KEY):
        return

    st.text_input(
        "Password",
        type="password",
        on_change=_password_entered,
        key=_PASSWORD_INPUT_KEY,
    )

    if st.session_state.get(_PASSWORD_STATE_KEY):
        return

    if st.session_state.get(_PASSWORD_ATTEMPTED_KEY, False):
        st.error("😕 Incorrect password")

    st.stop()
