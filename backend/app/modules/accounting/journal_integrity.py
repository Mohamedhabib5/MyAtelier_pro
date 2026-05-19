"""Journal entry integrity checks and utilities."""
from __future__ import annotations

import logging
from app.modules.accounting.models import JournalEntry

logger = logging.getLogger(__name__)


def warn_missing_branch(entry: JournalEntry) -> None:
    """Log a warning if a new journal entry is missing branch_id."""
    if entry.branch_id is None:
        logger.warning(
            "Journal entry %s (reference: %s, reference_type: %s) created without branch_id",
            entry.entry_number,
            entry.reference or "None",
            entry.reference_type or "manual",
        )
