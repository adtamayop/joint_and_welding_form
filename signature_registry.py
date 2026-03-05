import os
from typing import Optional

from config.signature_map import SIGNATURE_FILE_BY_PERSON


def get_signature_for_person(person_name: str) -> Optional[str]:
    if not person_name:
        return None
    configured = SIGNATURE_FILE_BY_PERSON.get(person_name, "")
    if not configured:
        return None
    path = configured if os.path.isabs(configured) else os.path.join(os.path.dirname(__file__), configured)
    return path if os.path.exists(path) else None
