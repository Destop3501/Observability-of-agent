"""
Inventory Management Agent

Executes a customer order workflow using these tools:
  1. Order management system   — create the order
  2. Inventory database         — verify stock
  3. Payment gateway            — collect payment
  4. Invoice generator          — generate invoice
  5. Delivery service           — arrange delivery
  6. Customer notification      — notify the customer

Usage:
    python agent.py                      # Run the full workflow (normal)
    python agent.py --fault inventory    # Inject inventory DB failure
    python agent.py --fault payment      # Inject payment timeout
    python agent.py --fault invoice      # Inject invoice error
    python agent.py --fault interrupt    # Interrupt agent mid-workflow
    python agent.py --fault delivery     # Inject delivery invalid response
    python agent.py --keys               # Print API key status
"""

import sys
from tools import (
    order_management_system,
    inventory_database,
    payment_gateway,
    invoice_generator,
    delivery_service,
    customer_notification,
    AgentInterruptedError,
)
from config import print_config_status


class InventoryManagementAgent:
    """Agent that orchestrates the order-fulfillment workflow."""

    def __init__(self, fault: str = None):
        """
        Args:
            fault: Which fault to inject for observability testing.
                   One of: None, "inventory", "payment", "invoice", "interrupt", "delivery"
        """
        self.fault = fault

    def process_order(self, customer_id: str, items: list, amount: float) -> dict:
        """
        Execute the full order workflow:
            Order → Stock → Payment → Invoice → Delivery → Notification
        """
        print(f"\n{'='*60}")
        print(f"  INVENTORY MANAGEMENT AGENT — STARTING WORKFLOW")
        print(f"  Customer : {customer_id}")
        print(f"  Items    : {items}")
        print(f"  Amount   : ${amount:.2f}")
        if self.fault:
            print(f"  ⚠️  Fault injection: {self.fault}")
        print(f"{'='*60}\n")

        results = {}

        # ── Step 1: Create Order ──
        print("Step 1/6 — Creating order...")
        order = order_management_system(
            customer_id, items,
            fault="unavailable" if self.fault == "inventory" else None
        )
        results["order"] = order
        print(f"  ✅ {order['message']}")
        order_id = order["order_id"]

        # ── Step 2: Verify Stock ──
        print("Step 2/6 — Verifying stock...")
        stock = inventory_database(
            order_id, items,
            fault="unavailable" if self.fault == "inventory" else None
        )
        results["stock"] = stock
        print(f"  ✅ {stock['message']}")
        print(f"     Stock levels: {stock['stock_levels']}")

        # ── Step 3: Collect Payment ──
        print("Step 3/6 — Collecting payment...")
        payment = payment_gateway(
            order_id, amount,
            fault="timeout" if self.fault == "payment" else None
        )
        results["payment"] = payment
        print(f"  ✅ {payment['message']}")

        # ── Step 4: Generate Invoice ──
        # Check for interrupt fault before this step
        if self.fault == "interrupt":
            print("Step 4/6 — Generating invoice...")
            print("  ⚠️  Agent interrupted before invoice generation!")
            raise AgentInterruptedError("Agent was interrupted after payment, before invoice generation.")

        print("Step 4/6 — Generating invoice...")
        invoice = invoice_generator(
            order_id, payment["transaction_id"], items, amount,
            fault="error" if self.fault == "invoice" else None
        )
        results["invoice"] = invoice
        print(f"  ✅ {invoice['message']}")

        # ── Step 5: Arrange Delivery ──
        print("Step 5/6 — Arranging delivery...")
        delivery = delivery_service(
            order_id, customer_id,
            fault="invalid" if self.fault == "delivery" else None
        )
        results["delivery"] = delivery
        print(f"  ✅ {delivery['message']}")

        # ── Step 6: Notify Customer ──
        print("Step 6/6 — Notifying customer...")
        notification_msg = (
            f"Your order {order_id} has been processed. "
            f"Invoice: {invoice['invoice_id']}. "
            f"Tracking: {delivery['tracking_number']}. "
            f"Estimated delivery: {delivery['estimated_delivery']}."
        )
        notification = customer_notification(customer_id, notification_msg)
        results["notification"] = notification
        print(f"  ✅ Notification sent to customer {customer_id} via {notification['channel']}.")

        print(f"\n{'='*60}")
        print(f"  WORKFLOW COMPLETE ✅")
        print(f"{'='*60}\n")

        return results


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

VALID_FAULTS = ["inventory", "payment", "invoice", "interrupt", "delivery"]

SAMPLE_ORDER = {
    "customer_id": "CUST-1001",
    "items": ["Laptop", "Mouse", "Keyboard"],
    "amount": 1299.99,
}


def main():
    fault = None

    if "--keys" in sys.argv:
        print_config_status()
        return

    if "--fault" in sys.argv:
        idx = sys.argv.index("--fault")
        if idx + 1 < len(sys.argv):
            fault = sys.argv[idx + 1]
            if fault not in VALID_FAULTS:
                print(f"Invalid fault: {fault}")
                print(f"Valid options: {', '.join(VALID_FAULTS)}")
                return

    agent = InventoryManagementAgent(fault=fault)

    try:
        agent.process_order(
            customer_id=SAMPLE_ORDER["customer_id"],
            items=SAMPLE_ORDER["items"],
            amount=SAMPLE_ORDER["amount"],
        )
    except AgentInterruptedError as e:
        print(f"\n{'='*60}")
        print(f"  WORKFLOW INTERRUPTED ⚠️")
        print(f"  Reason: {e}")
        print(f"{'='*60}\n")
    except ConnectionError as e:
        print(f"\n{'='*60}")
        print(f"  SERVICE UNAVAILABLE ❌")
        print(f"  Reason: {e}")
        print(f"{'='*60}\n")
    except TimeoutError as e:
        print(f"\n{'='*60}")
        print(f"  TIMEOUT ❌")
        print(f"  Reason: {e}")
        print(f"{'='*60}\n")
    except RuntimeError as e:
        print(f"\n{'='*60}")
        print(f"  SERVICE ERROR ❌")
        print(f"  Reason: {e}")
        print(f"{'='*60}\n")
    except ValueError as e:
        print(f"\n{'='*60}")
        print(f"  INVALID RESPONSE ❌")
        print(f"  Reason: {e}")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
