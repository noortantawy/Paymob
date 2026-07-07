"""Bank integration client.

`authorize_payment` posts an authorization request to the acquiring bank
(configured via ``settings.BANK_ENDPOINT``) and normalizes the response into a
decision dict the view can act on.
"""

import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

BANK_TIMEOUT = getattr(settings, "BANK_TIMEOUT", 10)


def authorize_payment(*, mid, tid, amount, currency, order_reference):
    """Call the bank endpoint and return its decision.

    Returns a dict: {"outcome": str, "auth_code": str | None, "reason": str | None}
    where ``outcome`` is one of "approved", "declined", or "timeout".

    The bank signals its decision via a ``status`` field in the JSON body
    ("accepted" / "rejected" / "timeout"), sent alongside HTTP 201 / 402 / 408
    respectively. We key off that body field rather than the HTTP status so a
    declined or timed-out payment is not mistaken for a network error. An actual
    network timeout (``BANK_TIMEOUT`` exceeded) is also reported as "timeout".
    """
    payload = {
        "mid": mid,
        "tid": tid,
        "amount": str(amount),
        "currency": currency,
        "order_reference": order_reference,
    }

    try:
        response = requests.post(
            settings.BANK_ENDPOINT, json=payload, timeout=BANK_TIMEOUT
        )
    except requests.Timeout:
        logger.warning("Bank request timed out for order %s", order_reference)
        return {"outcome": "timeout", "auth_code": None, "reason": "bank_timeout"}
    except requests.RequestException as exc:
        logger.error("Bank request failed for order %s: %s", order_reference, exc)
        return {"outcome": "declined", "auth_code": None, "reason": "bank_unreachable"}

    try:
        data = response.json()
    except ValueError:
        logger.error("Bank returned non-JSON response for order %s", order_reference)
        return {"outcome": "declined", "auth_code": None, "reason": "invalid_bank_response"}

    bank_status = data.get("status")
    if bank_status == "accepted":
        return {"outcome": "approved", "auth_code": data.get("auth_code"), "reason": None}
    if bank_status == "timeout":
        return {"outcome": "timeout", "auth_code": None, "reason": "bank_timeout"}
    if bank_status == "rejected":
        return {"outcome": "declined", "auth_code": None, "reason": "rejected"}

    logger.error(
        "Bank returned unexpected status %r for order %s", bank_status, order_reference
    )
    return {"outcome": "declined", "auth_code": None, "reason": "invalid_bank_response"}
