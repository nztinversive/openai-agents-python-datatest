from __future__ import annotations

import time
from collections.abc import Sequence
from typing import Any, Callable

DEFAULT_BASE_DELAY = 1.0
MAX_DELAY = 30.0


def _extract_result_conf(value: Any) -> tuple[Any, float]:
    """Return the result and confidence from ``value``.

    The callable passed to :func:`retry_with_fallbacks` can return either a
    tuple ``(result, confidence)`` or an object with a ``confidence``
    attribute. This helper normalizes the return value into a tuple.
    """
    if isinstance(value, tuple) and len(value) == 2:
        return value

    confidence = 0.0
    if hasattr(value, "confidence"):
        try:
            confidence = float(value.confidence)
        except (TypeError, ValueError):
            confidence = 0.0
    return value, confidence


def retry_with_fallbacks(
    agent_call: Callable[[Any], Any],
    model_chain: Sequence[Any],
    conf_threshold: float,
) -> Any:
    """Run ``agent_call`` across fallback models until the confidence threshold is met.

    ``agent_call`` is called with each model from ``model_chain`` in order. The
    callable should return either ``(result, confidence)`` or an object with a
    ``confidence`` attribute. If the returned confidence is greater than or equal
    to ``conf_threshold`` the result is returned immediately. Between failed
    attempts the function sleeps using exponential backoff.

    Args:
        agent_call: Callable invoked with the current model.
        model_chain: Sequence of models to try in order.
        conf_threshold: Minimum confidence required to succeed.

    Returns:
        The result from the first successful call.

    Raises:
        RuntimeError: If no call meets the confidence threshold.
    """

    delay = DEFAULT_BASE_DELAY
    for model in model_chain:
        try:
            result, confidence = _extract_result_conf(agent_call(model))
            if confidence >= conf_threshold:
                return result
        except Exception:
            pass
        time.sleep(delay)
        delay = min(delay * 2.0, MAX_DELAY)

    raise RuntimeError("All fallback models failed to meet the confidence threshold.")
