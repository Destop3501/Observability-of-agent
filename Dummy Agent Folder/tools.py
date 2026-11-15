"""
Tools used by the Inventory Management Agent.

Each tool simulates an external API call. The tools accept an optional
`fault` parameter so you can inject failures for observability testing:

  fault = "unavailable"   → service is down
  fault = "timeout"        → API call times out
  fault = "error"          → service returns an error
  fault = "invalid"        → service returns an invalid/unexpected response
  fault = "interrupt"       → raises AgentInterruptedError (mid-workflow)
  fault = None              → normal success
"""

import time
import random
from config import (
    ORDER_MGMT_API_KEY, INVENTORY_DB_API_KEY, PAYMENT_GATEWAY_API_KEY,
    INVOICE_GEN_API_KEY, DELIVERY_API_KEY, NOTIFICATION_API_KEY,
)


class AgentInterruptedError(Exception):
    """Raised when the agent is interrupted mid-execution."""
    pass


# ──────────────────────────────────────────────
# 1. Order Management System
# ──────────────────────────────────────────────

def order_management_system(customer_id: str, items: list, fault: str = None) -> dict:
    """Create an order in the order management system."""
    _check_key(ORDER_MGMT_API_KEY, "Order Management")
    _inject_fault(fault)

    order_id = f"ORD-{random.randint(10000, 99999)}"
    return {
        "order_id": order_id,
        "customer_id": customer_id,
        "items": items,
        "status": "created",
        "message": f"Order {order_id} created for customer {customer_id}.",
    }


# ──────────────────────────────────────────────
# 2. Inventory Database
# ──────────────────────────────────────────────

def inventory_database(order_id: str, items: list, fault: str = None) -> dict:
    """Verify stock levels for all items in the order."""
    _check_key(INVENTORY_DB_API_KEY, "Inventory DB")
    _inject_fault(fault)

    stock = {}
    for item in items:
        stock[item] = random.randint(1, 50)
    return {
        "order_id": order_id,
        "stock_verified": True,
        "stock_levels": stock,
        "message": f"Stock verified for order {order_id}.",
    }


# ──────────────────────────────────────────────
# 3. Payment Gateway
# ──────────────────────────────────────────────

def payment_gateway(order_id: str, amount: float, fault: str = None) -> dict:
    """Collect payment via the payment gateway."""
    _check_key(PAYMENT_GATEWAY_API_KEY, "Payment Gateway")
    _inject_fault(fault)

    transaction_id = f"TXN-{random.randint(100000, 999999)}"
    return {
        "order_id": order_id,
        "transaction_id": transaction_id,
        "amount": amount,
        "status": "paid",
        "message": f"Payment of ${amount:.2f} collected (txn {transaction_id}).",
    }


# ──────────────────────────────────────────────
# 4. Invoice Generator
# ──────────────────────────────────────────────

def invoice_generator(order_id: str, transaction_id: str, items: list, amount: float, fault: str = None) -> dict:
    """Generate an invoice for the order."""
    _check_key(INVOICE_GEN_API_KEY, "Invoice Generator")
    _inject_fault(fault)

    invoice_id = f"INV-{random.randint(10000, 99999)}"
    return {
        "order_id": order_id,
        "invoice_id": invoice_id,
        "transaction_id": transaction_id,
        "items": items,
        "total": amount,
        "message": f"Invoice {invoice_id} generated for order {order_id}.",
    }


# ──────────────────────────────────────────────
# 5. Delivery Service
# ──────────────────────────────────────────────

def delivery_service(order_id: str, customer_id: str, fault: str = None) -> dict:
    """Arrange delivery for the order."""
    _check_key(DELIVERY_API_KEY, "Delivery Service")
    _inject_fault(fault)

    tracking_number = f"TRK{random.randint(100000000, 999999999)}"
    return {
        "order_id": order_id,
        "tracking_number": tracking_number,
        "carrier": "FedEx",
        "estimated_delivery": "3-5 business days",
        "message": f"Delivery arranged. Tracking: {tracking_number}.",
    }


# ──────────────────────────────────────────────
# 6. Customer Notification Service
# ──────────────────────────────────────────────

def customer_notification(customer_id: str, message: str, fault: str = None) -> dict:
    """Send a notification to the customer."""
    _check_key(NOTIFICATION_API_KEY, "Notification Service")
    _inject_fault(fault)

    return {
        "customer_id": customer_id,
        "notification_sent": True,
        "message_sent": message,
        "channel": "email",
        "status": "sent",
    }


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _check_key(api_key: str, service_name: str):
    """Warn if an API key is not set."""
    if not api_key:
        print(f"  ⚠️  WARNING: {service_name} API key is not set. Using simulated response.")


def _inject_fault(fault: str):
    """Inject a fault into the tool call for observability testing."""
    if fault is None:
        return

    if fault == "unavailable":
        raise ConnectionError(f"Service is unavailable (simulated).")
    elif fault == "timeout":
        raise TimeoutError(f"API call timed out (simulated).")
    elif fault == "error":
        raise RuntimeError(f"Service returned an error (simulated).")
    elif fault == "invalid":
        raise ValueError(f"Service returned an invalid response (simulated).")
    elif fault == "interrupt":
        raise AgentInterruptedError(f"Agent interrupted mid-execution (simulated).")
