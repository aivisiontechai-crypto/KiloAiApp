#!/usr/bin/env python3
"""
LegalAI - Core Document Generator
AI-powered legal document generation using GPT-4
"""

import os
import json
import sqlite3
from datetime import datetime
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path
import asyncio

CONFIG = {
    "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
    "model": "gpt-4",
    "temperature": 0.3,
}


@dataclass
class GeneratedDocument:
    id: str
    user_id: int
    doc_type: str
    title: str
    content: str
    price: float
    created_at: str
    status: str


class LegalDocumentGenerator:
    """Generate legal documents using AI"""
    
    def __init__(self):
        self.doc_templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        return {
            "nda": {
                "name": "Non-Disclosure Agreement (NDA)",
                "description": "Protect your confidential information",
                "price": 29,
                "variables": ["disclosing_party", "receiving_party", "effective_date", "confidential_info", "duration", "governing_law"],
                "system_prompt": """You are a legal document expert. Generate a professional Non-Disclosure Agreement (NDA). Include: definitions, obligations, term, termination, remedies, governing law, and signatures."""
            },
            "service_contract": {
                "name": "Service Agreement",
                "description": "Contract for freelance services",
                "price": 39,
                "variables": ["client_name", "provider_name", "service_description", "payment_amount", "start_date", "duration"],
                "system_prompt": """You are a legal expert. Generate a professional Service Agreement. Include: parties, services scope, payment, timeline, deliverables, IP, confidentiality, termination, liability."""
            },
            "privacy_policy": {
                "name": "Privacy Policy",
                "description": "Required for websites and apps",
                "price": 49,
                "variables": ["company_name", "website_url", "contact_email", "data_collected", "cookies_usage"],
                "system_prompt": """You are a legal compliance expert. Generate a comprehensive Privacy Policy. Include: info collected, cookies, third-party services, GDPR/CCPA compliance."""
            },
            "terms_of_service": {
                "name": "Terms of Service",
                "description": "User agreement for your platform",
                "price": 49,
                "variables": ["company_name", "website_url", "service_description", "user_obligations", "payment_terms"],
                "system_prompt": """You are a legal expert. Generate Terms of Service. Include: acceptance, user accounts, IP, conduct, payment, disclaimer, liability, termination."""
            },
            "employment": {
                "name": "Employment Contract",
                "description": "Standard employment agreement",
                "price": 59,
                "variables": ["employer_name", "employee_name", "job_title", "salary", "benefits", "start_date"],
                "system_prompt": """You are a legal expert. Generate an Employment Agreement. Include: position, compensation, benefits, hours, confidentiality, non-compete, termination, IP assignment."""
            },
            "demand_letter": {
                "name": "Demand Letter",
                "description": "Formal demand for payment or action",
                "price": 34,
                "variables": ["sender_name", "recipient_name", "subject_matter", "amount_demanded", "deadline_days"],
                "system_prompt": """You are a legal professional. Generate a Demand Letter. Include: statement of facts, legal basis, specific demand, deadline, consequences."""
            },
            "invoice": {
                "name": "Professional Invoice",
                "description": "Custom invoice for your business",
                "price": 19,
                "variables": ["business_name", "client_name", "invoice_number", "items", "total_amount", "payment_deadline"],
                "system_prompt": """Generate a professional invoice template. Include: business details, client details, invoice number, line items, total, payment terms."""
            },
            "llc": {
                "name": "LLC Operating Agreement",
                "description": "Operating agreement for LLC",
                "price": 79,
                "variables": ["company_name", "member_names", "contributions", "profit_distribution", "management_structure"],
                "system_prompt": """You are a business lawyer. Generate an LLC Operating Agreement. Include: company name, members, capital contributions, profit allocation, management, voting, dissolution."""
            }
        }
    
    def get_available_docs(self) -> List[Dict]:
        return [
            {"id": key, "name": val["name"], "description": val["description"], "price": val["price"]}
            for key, val in self.doc_templates.items()
        ]
    
    async def generate_document(self, doc_type: str, variables: Dict[str, str]) -> str:
        template = self.doc_templates.get(doc_type)
        if not template:
            return f"Error: Unknown document type '{doc_type}'"
        
        variable_text = "\n".join([f"- {k}: {v}" for k, v in variables.items()])
        user_prompt = f"Generate a {template['name']} with:\n{variable_text}"
        
        if not CONFIG["openai_api_key"]:
            return self._generate_fallback(doc_type, variables, template)
        
        try:
            import openai
            openai.api_key = CONFIG["openai_api_key"]
            response = await openai.ChatCompletion.acreate(
                model=CONFIG["model"],
                messages=[
                    {"role": "system", "content": template["system_prompt"]},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=CONFIG["temperature"],
                max_tokens=4000
            )
            return response.choices[0].message.content
        except Exception as e:
            return self._generate_fallback(doc_type, variables, template)
    
    def _generate_fallback(self, doc_type: str, variables: Dict, template: Dict) -> str:
        templates = {
            "nda": f"""NON-DISCLOSURE AGREEMENT

Effective Date: {variables.get('effective_date', 'DATE')}

PARTIES:
Disclosing Party: {variables.get('disclosing_party', '[NAME]')}
Receiving Party: {variables.get('receiving_party', '[NAME]')}

1. CONFIDENTIAL INFORMATION
{variables.get('confidential_info', 'All proprietary information')}

2. OBLIGATIONS
The Receiving Party agrees to keep all information strictly confidential.

3. TERM
This Agreement is valid for {variables.get('duration', '2')} years.

4. GOVERNING LAW
Governed by {variables.get('governing_law', 'Delaware')} law.

_______________________          _______________________
Disclosing Party                Receiving Party
Date: _____________            Date: _____________""",

            "invoice": f"""INVOICE

Invoice #: {variables.get('invoice_number', 'INV-001')}
Date: {datetime.now().strftime('%Y-%m-%d')}

FROM: {variables.get('business_name', '[Business Name]')}
TO: {variables.get('client_name', '[Client Name]')}

Items: {variables.get('items', 'Services rendered')}
TOTAL: ${variables.get('total_amount', '0.00')}

Payment Deadline: {variables.get('payment_deadline', 'Net 30')}

Thank you!""",

            "privacy_policy": f"""PRIVACY POLICY

Last Updated: {datetime.now().strftime('%Y-%m-%d')}

{ variables.get('company_name', '[Company]')} ("we") operates {variables.get('website_url', '[Website]')}.

INFORMATION WE COLLECT:
{variables.get('data_collected', 'Personal information you provide')}

COOKIES:
{variables.get('cookies_usage', 'We use cookies')}

CONTACT: {variables.get('contact_email', 'contact@email.com')}""",
        }
        return templates.get(doc_type, f"Document: {template['name']}\n\nVariables:\n{variables}")


class DocumentDatabase:
    def __init__(self, db_path: str = "data/legalai.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY, username TEXT, platform TEXT, tier TEXT DEFAULT 'free',
            subscription_expires TEXT, documents_used INTEGER DEFAULT 0, lifetime_spent REAL DEFAULT 0, created_at TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY, user_id INTEGER, doc_type TEXT, title TEXT, content TEXT, price REAL, created_at TEXT, status TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, amount REAL, currency TEXT, plan TEXT,
            stripe_payment_id TEXT, created_at TEXT)''')
        conn.commit()
        conn.close()
    
    def add_user(self, user_id: int, username: str, platform: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('INSERT OR IGNORE INTO users (user_id, username, platform, created_at) VALUES (?, ?, ?, ?)',
            (user_id, username, platform, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = c.fetchone()
        conn.close()
        if row:
            return {"user_id": row[0], "username": row[1], "platform": row[2], "tier": row[3], 
                    "subscription_expires": row[4], "documents_used": row[5], "lifetime_spent": row[6], "created_at": row[7]}
        return None
    
    def save_document(self, doc: GeneratedDocument):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('INSERT INTO documents (id, user_id, doc_type, title, content, price, created_at, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (doc.id, doc.user_id, doc.doc_type, doc.title, doc.content, doc.price, doc.created_at, doc.status))
        c.execute('UPDATE users SET documents_used = documents_used + 1 WHERE user_id = ?', (doc.user_id,))
        conn.commit()
        conn.close()


if __name__ == "__main__":
    gen = LegalDocumentGenerator()
    print("\n📄 Available Documents:")
    for doc in gen.get_available_docs():
        print(f"  {doc['id']:15} ${doc['price']:2}  {doc['name']}")
