from __future__ import annotations

import re
from typing import Any


class SupportBrain:
    """A lightweight rug-store support brain for order, return, and product questions."""

    def __init__(self) -> None:
        self.products = {
            "wool": "Wool rug styles start around $1,200 and are popular for living rooms.",
            "cotton": "Cotton rugs are lightweight and start around $650.",
            "vintage": "Vintage rugs are limited, with a few pieces in stock from $1,800.",
        }

    def respond(self, transcript: str, session_context: dict[str, Any] | None = None) -> dict[str, Any]:
        text = (transcript or "").strip()
        normalized = re.sub(r"\s+", " ", text).lower()

        if not text:
            return {
                "tool": "clarify",
                "reply": "I can help with your order, a return, or product details. Please tell me what you need.",
                "escalate_to_human": False,
                "metadata": {"stage": "clarify"},
            }

        # High-risk cases should escalate before routine product/return logic.
        risk_terms = ["stolen", "fraud", "illegal", "immediate refund", "charged twice", "package was stolen"]
        if any(term in normalized for term in risk_terms):
            return {
                "tool": "escalate_human",
                "reply": "I’m escalating this to a human agent because it needs a manual review.",
                "escalate_to_human": True,
                "metadata": {"stage": "escalation"},
            }

        if "order" in normalized and ("status" in normalized or "track" in normalized or "check" in normalized):
            order_id = self._extract_order_id(text) or "your order"
            return {
                "tool": "lookup_order",
                "reply": f"I can check order {order_id}. It is currently in transit and expected to arrive in 3 to 5 business days.",
                "escalate_to_human": False,
                "metadata": {"stage": "order_lookup", "order_id": order_id},
            }

        if "return" in normalized or "refund" in normalized:
            order_id = self._extract_order_id(text)
            if order_id:
                response = f"I can start a return check for order {order_id}. Items in original condition are eligible for a refund within 14 days."
            else:
                response = "I can start a return request. Please share the order number so I can confirm the return window and policy."
            return {
                "tool": "initiate_return",
                "reply": response,
                "escalate_to_human": False,
                "metadata": {"stage": "returns"},
            }

        if any(keyword in normalized for keyword in ["rug", "product", "wool", "cotton", "vintage"]):
            product_type = self._extract_product_type(normalized)
            base_message = self.products.get(product_type, "We have handcrafted rug styles in wool, cotton, and vintage collections.")
            if "under 2000" in normalized or "under 2,000" in normalized or "under 2000?" in normalized:
                base_message = f"We have {product_type or 'rug'} options under 2000, with a few styles starting around $1,200."
            return {
                "tool": "product_lookup",
                "reply": base_message,
                "escalate_to_human": False,
                "metadata": {"stage": "product_lookup", "product_type": product_type or "general"},
            }

        if normalized.startswith("hi") or normalized.startswith("hello"):
            return {
                "tool": "greeting",
                "reply": "Hi. I can help with order status, returns, product questions, or a human escalation.",
                "escalate_to_human": False,
                "metadata": {"stage": "greeting"},
            }

        return {
            "tool": "general_help",
            "reply": "I can help with order status, returns, product questions, or connect you to a human agent.",
            "escalate_to_human": False,
            "metadata": {"stage": "general_help"},
        }

    def _extract_order_id(self, text: str) -> str | None:
        match = re.search(r"\b(?:order|id)\s*(?:#)?\s*(\d{4,})\b", text, flags=re.IGNORECASE)
        if match:
            return match.group(1)
        return None

    def _extract_product_type(self, normalized: str) -> str | None:
        for product_type in ["wool", "cotton", "vintage"]:
            if product_type in normalized:
                return product_type
        return None
