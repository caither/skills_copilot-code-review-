#!/usr/bin/env python
import sys
from pathlib import Path

import pytest


def main() -> None:
    """
    Debug/exploration helper for investigating import paths and module instances.

    This function is intentionally not executed during automated test runs.
    Run this file directly (``python test_imports.py``) to use it.
    """
    project_root = Path(__file__).resolve().parent
    src_path = project_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    print("Modules before any import:")
    db_modules = [k for k in sys.modules if "database" in k]
    print(f"  Database modules: {db_modules}")

    # Import conftest style.
    # NOTE: These imports intentionally use ``type: ignore[import]`` because this
    #       debug helper is executed directly with a manipulated ``sys.path``.
    #       Static type checkers running from the project root cannot reliably
    #       resolve these package-style imports in that context, but at runtime
    #       the imports succeed. This script is never imported by production
    #       code and is only used for manual debugging of import behaviour.
    import backend.database as db1  # type: ignore[import]

    print("\nAfter importing backend.database as db1:")
    db_modules = [k for k in sys.modules if "database" in k]
    print(f"  Database modules: {db_modules}")

    # Try src.backend.database
    try:
        import src.backend.database as db2  # type: ignore[import]
        print("\nImported src.backend.database")
        print(f"  db1 is db2: {db1 is db2}")
    except Exception as e:
        print(f"\nCouldn't import src.backend.database: {e}")

    # Now import app the way conftest does
    from app import app  # type: ignore[import]

    print("\nAfter importing app:")

    # Import config for dependency injection functions
    from backend.config import get_teachers_collection  # type: ignore[import]

    print(f"  get_teachers_collection: {get_teachers_collection}")
    print(f"  db1.teachers_collection: {type(db1.teachers_collection)}")

    # Get the collection via dependency injection
    teachers_collection = get_teachers_collection()
    print(
        f"  Same collection? {teachers_collection is db1.teachers_collection}"
    )


@pytest.mark.skip(
    reason="Debug exploration script; not part of automated test suite."
)
def test_imports_debug_script_placeholder() -> None:
    """
    Placeholder test to document that this file is a manual debug helper.

    The actual debug logic is only executed when this module is run as a script.
    """
    assert True


if __name__ == "__main__":
    main()
