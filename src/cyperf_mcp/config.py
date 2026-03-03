from __future__ import annotations

import json
import os
from pathlib import Path


class CyPerfConfig:
    """Loads and manages CyPerf configuration profiles."""

    def __init__(self, data: dict):
        self._data = data

    @classmethod
    def load(cls, path: str | None = None) -> "CyPerfConfig":
        """Load config from file.

        Resolution order:
        1. Explicit path argument
        2. CYPERF_CONFIG environment variable
        3. ~/.cyperf/config.json
        """
        if path is None:
            path = os.environ.get("CYPERF_CONFIG")
        if path is None:
            path = str(Path.home() / ".cyperf" / "config.json")

        config_path = Path(path)
        if not config_path.exists():
            raise FileNotFoundError(
                f"CyPerf config not found at {config_path}. "
                "Create it or set CYPERF_CONFIG env var."
            )

        with open(config_path) as f:
            data = json.load(f)

        return cls(data)

    def get_profile(self, name: str | None = None) -> dict:
        """Get a connection profile by name.

        Supports two formats:
        - Multi-profile: {"profiles": {"lab1": {...}}, "default_profile": "lab1"}
        - Single-profile shorthand: {"host": "...", "refresh_token": "..."}
        """
        if "profiles" in self._data:
            profiles = self._data["profiles"]
            if name is None:
                name = self._data.get("default_profile")
            if name is None:
                name = next(iter(profiles))
            if name not in profiles:
                raise KeyError(
                    f"Profile '{name}' not found. Available: {list(profiles.keys())}"
                )
            profile = profiles[name]
        else:
            profile = self._data

        if "host" not in profile:
            raise ValueError("Profile must contain 'host' field")
        has_auth = (
            "refresh_token" in profile
            or ("username" in profile and "password" in profile)
        )
        if not has_auth:
            raise ValueError(
                "Profile must contain 'refresh_token' or 'username'+'password'"
            )

        return profile

    @property
    def profile_names(self) -> list[str]:
        if "profiles" in self._data:
            return list(self._data["profiles"].keys())
        return ["default"]
