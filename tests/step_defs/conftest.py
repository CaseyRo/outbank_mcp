"""Conftest for BDD step definitions - imports fixtures from mcp.conftest."""

import sys
from pathlib import Path

# Add parent directory to path to import from tests.mcp.conftest
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import all fixtures from mcp.conftest so they're available to step definitions
from mcp.conftest import *  # noqa: F401, F403
