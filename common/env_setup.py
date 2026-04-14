import os
from .config import (
    GOOGLE_API_KEY,
)

def apply_env():
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
    # Some Gemini SDKs still look for this alias.
    os.environ.setdefault("GEMINI_API_KEY", GOOGLE_API_KEY)

