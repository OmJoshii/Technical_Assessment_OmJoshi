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