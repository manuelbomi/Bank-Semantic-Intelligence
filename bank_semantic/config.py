"""Shared filesystem configuration and demo authorization scopes."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "generated"
ARTIFACTS = ROOT / "artifacts"
# These scopes are educational; production authentication is external.
SCOPES = {
    "hr": {"hr", "policy"},
    "executive": {"aggregate", "policy", "partnership"},
    "analyst": {"aggregate", "policy", "graph"},
    "fraud": {"aggregate", "policy", "graph", "investigate"},
    "developer": {"aggregate", "policy", "graph"},
    "customer": {"own_accounts", "policy"},
}
