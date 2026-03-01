#!/usr/bin/env python3
"""SignalAI - Admin Dashboard"""
import sqlite3
from pathlib import Path
from typing import Dict, List

class AdminDashboard:
    def __init__(self, db_path="data/signalai.db"): self.db_path = db_path
    
    def get_stats(self) -> Dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users"); users = c.fetchone()[0] or 0
        c.execute("SELECT tier, COUNT(*) FROM users GROUP BY tier"); tiers = {r[0]: r[1] for r in c.fetchall()}
        c.execute("SELECT SUM(amount) FROM payments"); revenue = c.fetchone()[0] or 0
        c.execute("SELECT COUNT(*) FROM signals"); signals = c.fetchone()[0] or 0
        c.execute("SELECT signal_type, COUNT(*) FROM signals GROUP BY signal_type"); signal_types = {r[0]: r[1] for r in c.fetchall()}
        conn.close()
        return {"users": users, "tiers": tiers, "revenue": revenue, "signals": signals, "signal_types": signal_types}
    
    def print_dashboard(self):
        s = self.get_stats()
        print("\n" + "="*50)
        print("📈  SIGNALAI ADMIN")
        print("="*50)
        print(f"Users: {s['users']} | Revenue: ${s['revenue']:.2f}")
        print(f"Signals: {s['signals']} | Tiers: {s['tiers']}")
        print("\n📊 Signal Types:")
        for t, c in s['signal_types'].items(): print(f"  {t}: {c}")
        print("="*50)

if __name__ == "__main__": AdminDashboard().print_dashboard()
