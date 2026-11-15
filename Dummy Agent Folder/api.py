"""
Flask API server for the Inventory Management Agent.

Exposes REST endpoints that the frontend calls.

Run:
    .\\venv\\Scripts\\python.exe api.py

Endpoints:
    GET  /api/health          → health check
    GET  /api/keys             → API key status
    GET  /api/tools            → list all available tools
    POST /api/process-order    → run the full workflow (optionally inject a fault)

    Individual tool endpoints:
    POST /api/tool/order       → Order Management System
    POST /api/tool/inventory    → Inventory Database
    POST /api/tool/payment      → Payment Gateway
    POST /api/tool/invoice      → Invoice Generator
    POST /api/tool/delivery     → Delivery Service
    POST /api/tool/notification → Customer Notification
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from config import print_config_status, ORDER_MGMT_API_KEY, INVENTORY_DB_API_KEY, PAYMENT_GATEWAY_API_KEY, INVOICE_GEN_API_KEY, DELIVERY_API_KEY, NOTIFICATION_API_KEY
from tools import (
    order_management_system,
    inventory_database,
    payment_gateway,
    invoice_generator,
    delivery_service,
    customer_notification,
    AgentInterruptedError,
)
import traceback

app = Flask(__name__)
CORS(app)

VALID_FAULTS = ["none", "inventory", "payment", "invoice", "interrupt", "delivery"]

FAULT_MAP = {
    "inventory": "unavailable",
    "payment": "timeout",
    "invoice": "error",
    "interrupt": "interrupt",
    "delivery": "invalid",
}


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "inventory-management-agent"})


@app.route("/api/keys", methods=["GET"])
def keys():
    return jsonify({
        "ORDER_MGMT_API_KEY":     bool(ORDER_MGMT_API_KEY),
        "INVENTORY_DB_API_KEY":   bool(INVENTORY_DB_API_KEY),
        "PAYMENT_GATEWAY_API_KEY": bool(PAYMENT_GATEWAY_API_KEY),
        "INVOICE_GEN_API_KEY":    bool(INVOICE_GEN_API_KEY),
        "DELIVERY_API_KEY":       bool(DELIVERY_API_KEY),
        "NOTIFICATION_API_KEY":   bool(NOTIFICATION_API_KEY),
    })


@app.route("/api/tools", methods=["GET"])
def tools():
    return jsonify({
        "tools": [
            {"id": 1, "name": "Order Management System",   "description": "Create and manage customer orders"},
            {"id": 2, "name": "Inventory Database",         "description": "Verify stock levels for ordered items"},
            {"id": 3, "name": "Payment Gateway",            "description": "Collect payment from customer"},
            {"id": 4, "name": "Invoice Generator",          "description": "Generate invoice for the order"},
            {"id": 5, "name": "Delivery Service",           "description": "Arrange delivery and get tracking number"},
            {"id": 6, "name": "Customer Notification",      "description": "Send order confirmation to customer"},
        ],
        "faults": [
            {"id": "none",      "label": "No Fault (Normal)",           "description": "All steps succeed"},
            {"id": "inventory", "label": "Inventory DB Unavailable",    "description": "Inventory database becomes unavailable"},
            {"id": "payment",   "label": "Payment API Timeout",         "description": "Payment gateway times out"},
            {"id": "invoice",   "label": "Invoice Generator Error",    "description": "Invoice generator returns an error"},
            {"id": "interrupt", "label": "Agent Interrupted",           "description": "Agent interrupted mid-execution"},
            {"id": "delivery",  "label": "Delivery Invalid Response",  "description": "Delivery service returns invalid response"},
        ],
    })


@app.route("/api/process-order", methods=["POST"])
def process_order():
    data = request.json or {}
    customer_id = data.get("customer_id", "CUST-1001")
    items = data.get("items", ["Laptop", "Mouse", "Keyboard"])
    amount = data.get("amount", 1299.99)
    fault = data.get("fault", "none")

    if fault not in VALID_FAULTS:
        return jsonify({"error": f"Invalid fault. Valid options: {VALID_FAULTS}"}), 400

    steps = []
    fault_type = FAULT_MAP.get(fault) if fault != "none" else None

    def add_step(step_num, name, status, data=None, error=None):
        steps.append({
            "step": step_num,
            "name": name,
            "status": status,
            "data": data,
            "error": error,
        })

    try:
        # Step 1: Order Management
        add_step(1, "Order Management System", "running")
        order = order_management_system(customer_id, items)
        steps[-1]["status"] = "success"
        steps[-1]["data"] = order
        order_id = order["order_id"]

        # Step 2: Inventory Database
        add_step(2, "Inventory Database", "running")
        stock = inventory_database(order_id, items, fault=fault_type if fault == "inventory" else None)
        steps[-1]["status"] = "success"
        steps[-1]["data"] = stock

        # Step 3: Payment Gateway
        add_step(3, "Payment Gateway", "running")
        payment = payment_gateway(order_id, amount, fault=fault_type if fault == "payment" else None)
        steps[-1]["status"] = "success"
        steps[-1]["data"] = payment

        # Step 4: Invoice Generator
        if fault == "interrupt":
            add_step(4, "Invoice Generator", "interrupted",
                     error="Agent interrupted before invoice generation.")
            return jsonify({
                "success": False,
                "customer_id": customer_id,
                "steps": steps,
                "error_type": "interrupted",
                "message": "Agent was interrupted mid-execution.",
            }), 200

        add_step(4, "Invoice Generator", "running")
        invoice = invoice_generator(order_id, payment["transaction_id"], items, amount,
                                    fault=fault_type if fault == "invoice" else None)
        steps[-1]["status"] = "success"
        steps[-1]["data"] = invoice

        # Step 5: Delivery Service
        add_step(5, "Delivery Service", "running")
        delivery = delivery_service(order_id, customer_id,
                                    fault=fault_type if fault == "delivery" else None)
        steps[-1]["status"] = "success"
        steps[-1]["data"] = delivery

        # Step 6: Customer Notification
        add_step(6, "Customer Notification", "running")
        notification_msg = (
            f"Your order {order_id} has been processed. "
            f"Invoice: {invoice['invoice_id']}. "
            f"Tracking: {delivery['tracking_number']}. "
            f"Estimated delivery: {delivery['estimated_delivery']}."
        )
        notification = customer_notification(customer_id, notification_msg)
        steps[-1]["status"] = "success"
        steps[-1]["data"] = notification

        return jsonify({
            "success": True,
            "customer_id": customer_id,
            "steps": steps,
            "message": "Order processed successfully.",
        }), 200

    except AgentInterruptedError as e:
        return jsonify({
            "success": False,
            "customer_id": customer_id,
            "steps": steps,
            "error_type": "interrupted",
            "message": str(e),
        }), 200

    except ConnectionError as e:
        # Find the running step and mark it failed
        for s in steps:
            if s["status"] == "running":
                s["status"] = "failed"
                s["error"] = str(e)
        return jsonify({
            "success": False,
            "customer_id": customer_id,
            "steps": steps,
            "error_type": "unavailable",
            "message": str(e),
        }), 200

    except TimeoutError as e:
        for s in steps:
            if s["status"] == "running":
                s["status"] = "failed"
                s["error"] = str(e)
        return jsonify({
            "success": False,
            "customer_id": customer_id,
            "steps": steps,
            "error_type": "timeout",
            "message": str(e),
        }), 200

    except RuntimeError as e:
        for s in steps:
            if s["status"] == "running":
                s["status"] = "failed"
                s["error"] = str(e)
        return jsonify({
            "success": False,
            "customer_id": customer_id,
            "steps": steps,
            "error_type": "error",
            "message": str(e),
        }), 200

    except ValueError as e:
        for s in steps:
            if s["status"] == "running":
                s["status"] = "failed"
                s["error"] = str(e)
        return jsonify({
            "success": False,
            "customer_id": customer_id,
            "steps": steps,
            "error_type": "invalid",
            "message": str(e),
        }), 200

    except Exception as e:
        for s in steps:
            if s["status"] == "running":
                s["status"] = "failed"
                s["error"] = str(e)
        return jsonify({
            "success": False,
            "customer_id": customer_id,
            "steps": steps,
            "error_type": "unknown",
            "message": str(e),
        }), 500


# ──────────────────────────────────────────────
# Individual Tool Endpoints
# Each can be called standalone with optional fault injection.
# ──────────────────────────────────────────────

def _tool_response(func, *args, **kwargs):
    """Helper: run a tool and return a standard JSON response."""
    try:
        result = func(*args, **kwargs)
        return jsonify({"success": True, "data": result, "error": None}), 200
    except AgentInterruptedError as e:
        return jsonify({"success": False, "data": None, "error": str(e), "error_type": "interrupted"}), 200
    except ConnectionError as e:
        return jsonify({"success": False, "data": None, "error": str(e), "error_type": "unavailable"}), 200
    except TimeoutError as e:
        return jsonify({"success": False, "data": None, "error": str(e), "error_type": "timeout"}), 200
    except RuntimeError as e:
        return jsonify({"success": False, "data": None, "error": str(e), "error_type": "error"}), 200
    except ValueError as e:
        return jsonify({"success": False, "data": None, "error": str(e), "error_type": "invalid"}), 200
    except Exception as e:
        return jsonify({"success": False, "data": None, "error": str(e), "error_type": "unknown"}), 500


@app.route("/api/tool/order", methods=["POST"])
def tool_order():
    """Tool 1: Order Management System — create an order."""
    data = request.json or {}
    customer_id = data.get("customer_id", "CUST-1001")
    items = data.get("items", ["Laptop", "Mouse", "Keyboard"])
    fault = data.get("fault")
    return _tool_response(order_management_system, customer_id, items, fault=fault)


@app.route("/api/tool/inventory", methods=["POST"])
def tool_inventory():
    """Tool 2: Inventory Database — verify stock."""
    data = request.json or {}
    order_id = data.get("order_id", "ORD-00000")
    items = data.get("items", ["Laptop", "Mouse", "Keyboard"])
    fault = data.get("fault")
    return _tool_response(inventory_database, order_id, items, fault=fault)


@app.route("/api/tool/payment", methods=["POST"])
def tool_payment():
    """Tool 3: Payment Gateway — collect payment."""
    data = request.json or {}
    order_id = data.get("order_id", "ORD-00000")
    amount = float(data.get("amount", 1299.99))
    fault = data.get("fault")
    return _tool_response(payment_gateway, order_id, amount, fault=fault)


@app.route("/api/tool/invoice", methods=["POST"])
def tool_invoice():
    """Tool 4: Invoice Generator — generate invoice."""
    data = request.json or {}
    order_id = data.get("order_id", "ORD-00000")
    transaction_id = data.get("transaction_id", "TXN-000000")
    items = data.get("items", ["Laptop", "Mouse", "Keyboard"])
    amount = float(data.get("amount", 1299.99))
    fault = data.get("fault")
    return _tool_response(invoice_generator, order_id, transaction_id, items, amount, fault=fault)


@app.route("/api/tool/delivery", methods=["POST"])
def tool_delivery():
    """Tool 5: Delivery Service — arrange delivery."""
    data = request.json or {}
    order_id = data.get("order_id", "ORD-00000")
    customer_id = data.get("customer_id", "CUST-1001")
    fault = data.get("fault")
    return _tool_response(delivery_service, order_id, customer_id, fault=fault)


@app.route("/api/tool/notification", methods=["POST"])
def tool_notification():
    """Tool 6: Customer Notification — send notification."""
    data = request.json or {}
    customer_id = data.get("customer_id", "CUST-1001")
    message = data.get("message", "Your order has been processed.")
    fault = data.get("fault")
    return _tool_response(customer_notification, customer_id, message, fault=fault)


if __name__ == "__main__":
    print("\n" + "="*50)
    print("  Inventory Management Agent API")
    print("  Running on http://localhost:5000")
    print("="*50 + "\n")
    app.run(host="0.0.0.0", port=5000, debug=True)
