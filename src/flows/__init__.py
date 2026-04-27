"""Reusable business-logic flows.

Each module wraps a multi-step user journey that would otherwise be
duplicated across test files.  Tests only call flows; page-level details
stay inside the page-object layer.

The :class:`Flows` façade class is the primary public API — tests use it
via the ``flows`` pytest fixture and never import individual flow modules.
"""

from flows.flows import Flows

__all__ = ["Flows"]
