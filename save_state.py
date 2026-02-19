import json
import os
from datetime import date, datetime
from typing import Any, Dict

import streamlit as st

STATE_DIR = os.path.join(os.path.dirname(__file__), "generated_reports")
STATE_FILE = os.path.join(STATE_DIR, "saved_session_state.json")

_RESTORE_FLAG = "_saved_state_restored"

_EXACT_ALLOWED = {
    "datos_proyecto",
    "norma_global",
}

_ALLOWED_PREFIXES = (
    "bloque_",
    "procedimiento_",
    "materiales_",
    "procesos_",
    "tipos_",
    "tabla_",
    "estandares_",
    "parametros_",
    "resultados_",
    "tipo_metodo_",
    "proceso_corriente_",
    "palpador_",
    "frecuencias_",
    "elementos_",
    "modulo_",
)

_BLOCKED_PREFIXES = (
    "_",
    "imagenes",
    "esquema_",
    "delete_idx",
)

_BLOCKED_EXACT = {
    "pages_config",
    "esquema_elementos_global",
}


def _is_upload_like(value: Any) -> bool:
    return hasattr(value, "read") and hasattr(value, "name")


def _serialize(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, date) and not isinstance(value, datetime):
        return {"__type__": "date", "value": value.isoformat()}

    if isinstance(value, datetime):
        return {"__type__": "datetime", "value": value.isoformat()}

    if isinstance(value, dict):
        out: Dict[str, Any] = {}
        for key, item in value.items():
            if key == "archivo":
                # Uploaded files cannot be restored after reload.
                continue
            serialized = _serialize(item)
            if serialized is not None:
                out[key] = serialized
        return out

    if isinstance(value, (list, tuple, set)):
        items = []
        for item in value:
            serialized = _serialize(item)
            if serialized is not None:
                items.append(serialized)
        return items

    if _is_upload_like(value):
        return None

    return str(value)


def _deserialize(value: Any) -> Any:
    if isinstance(value, dict):
        t = value.get("__type__")
        if t == "date":
            try:
                return date.fromisoformat(value["value"])
            except Exception:
                return value.get("value")
        if t == "datetime":
            try:
                return datetime.fromisoformat(value["value"])
            except Exception:
                return value.get("value")
        return {k: _deserialize(v) for k, v in value.items()}

    if isinstance(value, list):
        return [_deserialize(v) for v in value]

    return value


def _should_persist_key(key: str) -> bool:
    if key in _BLOCKED_EXACT:
        return False

    for prefix in _BLOCKED_PREFIXES:
        if key.startswith(prefix):
            return False

    if key in _EXACT_ALLOWED:
        return True

    for prefix in _ALLOWED_PREFIXES:
        if key.startswith(prefix):
            return True

    return False


def persist_session_state() -> None:
    os.makedirs(STATE_DIR, exist_ok=True)

    state = {}
    for key, value in st.session_state.items():
        if not _should_persist_key(key):
            continue
        serialized = _serialize(value)
        if serialized is not None:
            state[key] = serialized

    payload = {
        "saved_at": datetime.now().isoformat(),
        "state": state,
    }

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def restore_session_state() -> bool:
    if st.session_state.get(_RESTORE_FLAG):
        return False

    st.session_state[_RESTORE_FLAG] = True

    if not os.path.exists(STATE_FILE):
        return False

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except (OSError, json.JSONDecodeError):
        return False

    state = payload.get("state", {}) if isinstance(payload, dict) else {}
    if not isinstance(state, dict):
        return False

    for key, value in state.items():
        if key not in st.session_state:
            st.session_state[key] = _deserialize(value)

    return True


def get_saved_at() -> str:
    if not os.path.exists(STATE_FILE):
        return ""

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except (OSError, json.JSONDecodeError):
        return ""

    if isinstance(payload, dict):
        return str(payload.get("saved_at", ""))
    return ""
