#!/usr/bin/env python3
"""
LegalAI - Stripe Payment Integration
"""

import os
import stripe
from datetime import datetime, timedelta
from pathlib import Path

stripe.api_key = os.getenv("STRIPE_API_KEY", "")

PRICES = {"pro": 2900, "business": 9900}


class PaymentProcessor:
    def __init__(self, db_path: str = "data/legalai.db"):
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
                        "product_data": {"name": f"LegalAI {plan.title()} Plan"},
                        "unit_amount": PRICES.get(plan, 2900),
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
    
    def handle_webhook(self, payload: bytes, signature: str, webhook_secret: str):
        if not stripe.api_key:
            return {"status": "ignored"}
        
        try:
            event = stripe.Webhook.construct_event(payload, signature, webhook_secret)
            
            if event["type"] == "checkout.session.completed":
                session = event["data"]["object"]
                self._update_subscription(session)
            
            return {"status": "success"}
        except:
            return {"status": "error"}
    
    def _update_subscription(self, session: dict):
        import sqlite3
        user_id = session.get("metadata", {}).get("user_id")
        plan = session.get("metadata", {}).get("plan", "pro")
        
        if user_id:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            expires = (datetime.now() + timedelta(days=30)).isoformat()
            c.execute("UPDATE users SET tier = ?, subscription_expires = ? WHERE user_id = ?", 
                     (plan, expires, int(user_id)))
            c.execute("INSERT INTO payments (user_id, amount, plan, created_at) VALUES (?, ?, ?, ?)",
                     (int(user_id), PRICES.get(plan, 2900)/100, plan, datetime.now().isoformat()))
            conn.commit()
            conn.close()


if __name__ == "__main__":
    print("💳 Payment Processor Ready")
    print(f"   Pro: ${PRICES['pro']/100}/mo")
    print(f"   Business: ${PRICES['business']/100}/mo")
