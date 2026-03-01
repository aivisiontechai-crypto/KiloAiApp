#!/usr/bin/env python3
"""SignalAI - Payment Processor"""
import os, stripe
stripe.api_key = os.getenv("STRIPE_API_KEY", "")
PRICES = {"pro": 1900, "vip": 4900}

class PaymentProcessor:
    def __init__(self, db_path="data/signalai.db"): self.db_path = db_path
    
    def create_checkout(self, user_id: int, plan: str) -> str:
        if not stripe.api_key: return "https://example.com/pay"
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{"price_data": {"currency": "usd", "product_data": {"name": f"SignalAI {plan.title()}"}, "unit_amount": PRICES.get(plan, 1900), "recurring": {"interval": "month"}}, "quantity": 1}],
                mode="subscription", success_url="https://yoursite.com/success", cancel_url="https://yoursite.com/cancel",
                metadata={"user_id": str(user_id), "plan": plan})
            return session.url
        except: return "https://example.com/pay"

if __name__ == "__main__":
    print("💳 SignalAI Payments Ready")
    print(f"   Pro: ${PRICES['pro']/100}/mo")
    print(f"   VIP: ${PRICES['vip']/100}/mo")
