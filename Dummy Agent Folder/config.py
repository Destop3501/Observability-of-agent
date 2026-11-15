"""
Configuration for the Inventory Management Agent.
All API keys are read from environment variables.
Copy `.env.example` to `.env` and fill in your real keys.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# 1. Order Management System
ORDER_MGMT_API_KEY    = os.getenv("ORDER_MGMT_API_KEY", "")
ORDER_MGMT_BASE_URL   = os.getenv("ORDER_MGMT_BASE_URL", "https://api.ordermgmt.example.com/v1")

# 2. Inventory Database
INVENTORY_DB_API_KEY  = os.getenv("INVENTORY_DB_API_KEY", "")
INVENTORY_DB_BASE_URL = os.getenv("INVENTORY_DB_BASE_URL", "https://api.inventory.example.com/v1")

# 3. Payment Gateway (e.g., Stripe)
PAYMENT_GATEWAY_API_KEY    = os.getenv("PAYMENT_GATEWAY_API_KEY", "")
PAYMENT_GATEWAY_BASE_URL   = os.getenv("PAYMENT_GATEWAY_BASE_URL", "https://api.payment.example.com/v1")

# 4. Invoice Generator
INVOICE_GEN_API_KEY    = os.getenv("INVOICE_GEN_API_KEY", "")
INVOICE_GEN_BASE_URL   = os.getenv("INVOICE_GEN_BASE_URL", "https://api.invoicegen.example.com/v1")

# 5. Delivery Service (e.g., FedEx / UPS)
DELIVERY_API_KEY    = os.getenv("DELIVERY_API_KEY", "")
DELIVERY_BASE_URL   = os.getenv("DELIVERY_BASE_URL", "https://api.delivery.example.com/v1")

# 6. Customer Notification Service (e.g., SendGrid / Twilio)
NOTIFICATION_API_KEY    = os.getenv("NOTIFICATION_API_KEY", "")
NOTIFICATION_BASE_URL   = os.getenv("NOTIFICATION_BASE_URL", "https://api.notify.example.com/v1")


def print_config_status():
    """Print which API keys are present vs missing."""
    keys = {
        "ORDER_MGMT_API_KEY":     ORDER_MGMT_API_KEY,
        "INVENTORY_DB_API_KEY":   INVENTORY_DB_API_KEY,
        "PAYMENT_GATEWAY_API_KEY": PAYMENT_GATEWAY_API_KEY,
        "INVOICE_GEN_API_KEY":    INVOICE_GEN_API_KEY,
        "DELIVERY_API_KEY":       DELIVERY_API_KEY,
        "NOTIFICATION_API_KEY":   NOTIFICATION_API_KEY,
    }
    print("\n=== API Key Status ===")
    for name, val in keys.items():
        status = "✅ SET" if val else "❌ MISSING"
        print(f"  {name}: {status}")
    print()
