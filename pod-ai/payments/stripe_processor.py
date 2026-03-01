#!/usr/bin/env python3
"""
PodAI - Payment Processor
"""

import os
import stripe
from datetime import datetime, timedelta

stripe.api_key = os.getenv("STRIPE_API_KEY", "")

PRICES = {"pro": 1200, "business": 4900}


class PaymentProcessor:
    def __init__(self, db_path: str = "data/podai.db"):
        self.db_path = db_path
    
    def create_checkout(self, user_id: int, plan: str) -> str:
        if not stripe.api_key:
            return "https://example.com/pay"
        
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": f"PodAI {plan.title()}"},
                        "unit_amount": PRICES.get(plan, 1200),
                        "recurring": {"interval": "month"}
                    },
                    "quantity": 1
                }],
                mode="subscription",
                success_url="https://yoursite.com/success",
                cancel_url="https://yoursite.com/cancel",
                metadata={"user_id": str(user_id), "plan": plan}
            )
            return session.url
        except:
            return "https://example.com/pay"


if __name__ == "__main__":
    print("💳 PodAI Payments Ready")
    print(f"   Pro: ${PRICES['pro']/100}/mo")
    print(f"   Business: ${PRICES['business']/100}/mo")
