import json
import copy

products = [
    {"product_id": "P1", "name": "Shampoo",    "stock": 10},
    {"product_id": "P2", "name": "Soap",       "stock": 20},
    {"product_id": "P3", "name": "Toothpaste", "stock": 15},
]

order = {
    "order_id": "O1001",
    "items": [
        {"product_id": "P1", "quantity": 2},
        {"product_id": "P2", "quantity": 5},
    ],
}


def process_order(products, order):
    order_id = order["order_id"]
    items = order["items"]

    # Edge Case 1: Empty order
    if not items:
        return {"status": "error", "order_id": order_id, "message": "Order has no items."}

    # Build a dictionary for quick product lookup
    inventory = {p["product_id"]: p for p in products}

    # Edge Case 2: Merge duplicate product IDs by combining their quantities
    merged = {}
    for item in items:
        pid = item["product_id"]
        qty = item["quantity"]
        merged[pid] = merged.get(pid, 0) + qty

    # Edge Case 3: Invalid quantity
    for pid, qty in merged.items():
        if qty <= 0:
            return {"status": "error", "order_id": order_id, "message": f"Quantity for '{pid}' must be greater than zero."}

    # Edge Case 4: Product does not exist
    for pid in merged:
        if pid not in inventory:
            return {"status": "error", "order_id": order_id, "message": f"Product '{pid}' not found in inventory."}

    # Edge Case 5: Requested quantity exceeds available stock
    for pid, qty in merged.items():
        available = inventory[pid]["stock"]
        if qty > available:
            name = inventory[pid]["name"]
            return {"status": "error", "order_id": order_id, "message": f"Not enough stock for '{name}'. Requested: {qty}, Available: {available}."}

    # All checks passed — deduct stock
    for pid, qty in merged.items():
        inventory[pid]["stock"] -= qty

    updated_stock = [{"product_id": p["product_id"], "name": p["name"], "stock": p["stock"]} for p in products]

    return {"status": "success", "order_id": order_id, "message": f"Order {order_id} placed successfully.", "updated_stock": updated_stock}

# --- Tests ---

test_cases = [
    ("Successful order",           {"order_id": "O1001", "items": [{"product_id": "P1", "quantity": 2}, {"product_id": "P2", "quantity": 5}]}),
    ("Product not found",          {"order_id": "O1002", "items": [{"product_id": "P99", "quantity": 1}]}),
    ("Quantity exceeds stock",     {"order_id": "O1003", "items": [{"product_id": "P1", "quantity": 100}]}),
    ("Empty order",                {"order_id": "O1004", "items": []}),
    ("Duplicate product entries",  {"order_id": "O1005", "items": [{"product_id": "P1", "quantity": 4}, {"product_id": "P1", "quantity": 4}]}),
    ("Invalid quantity",           {"order_id": "O1006", "items": [{"product_id": "P1", "quantity": -1}]}),
]

for label, test_order in test_cases:
    print(f"\n--- {label} ---")
    print(json.dumps(process_order(copy.deepcopy(products), test_order), indent=2))