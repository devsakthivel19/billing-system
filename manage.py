#!/usr/bin/env python
"""Django command-line utility for administrative tasks."""

from __future__ import annotations

import os
import sys


def main() -> None:
    """Run Django administrative commands."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Make sure dependencies are installed and "
            "the virtual environment is activated."
        ) from exc

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
