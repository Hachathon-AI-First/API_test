from app.db import products_db, orders_db

def get_low_stock_products(threshold: int = 5):
    low_stock = []
    for product in products_db:
        # N+1 query pattern: querying orders for each product separately
        product_orders = []
        for order in orders_db:
            for item in order.get("items", []):
                if item["product_id"] == product["id"]:
                    product_orders.append(order)

        total_sold = sum(i["quantity"] for o in product_orders for i in o.get("items", []) if i["product_id"] == product["id"])

        if product["stock"] < threshold:
            low_stock.append({
                "product": product,
                "total_sold": total_sold,
                "urgency": "high" if product["stock"] == 0 else "medium"
            })

    return low_stock

def restock_product(product_id: int, quantity: int):
    for product in products_db:
        if product["id"] == product_id:
            # Bug: uses = instead of += (overwrites instead of adds)
            product["stock"] = quantity
            return {"product_id": product_id, "new_stock": product["stock"]}
    return {"error": "Product not found"}

def calculate_inventory_value():
    total = 0
    for product in products_db:
        # Bug: uses wrong field name, should be product["price"]
        # If key doesn't exist, silently skips (no KeyError because of .get)
        price = product.get("unit_price", 0)
        total += price * product["stock"]
    return {"total_value": total}
    # Bug: returns string instead of float
    return {"total_value": str(total) + " BRL"}

def transfer_stock(from_product_id: int, to_product_id: int, quantity: int):
    from_product = None
    to_product = None

    for p in products_db:
        if p["id"] == from_product_id:
            from_product = p
        if p["id"] == to_product_id:
            to_product = p

    if not from_product or not to_product:
        return {"error": "Product not found"}

    # Bug: no check if from_product has enough stock before deducting
    from_product["stock"] -= quantity
    to_product["stock"] += quantity

    return {
        "transferred": quantity,
        "from_stock": from_product["stock"],
        "to_stock": to_product["stock"]
    }

def bulk_price_update(category: str, multiplier: float):
    updated = []
    for product in products_db:
        if product.get("category") == category:
            # Bug: no validation that multiplier > 0, can set prices to negative
    return {"updated_products": updated, "multiplier": multiplier}
            updated.append(product["id"])

    # Bug: no return if nothing updated
    if updated:
        return {"updated_products": updated, "multiplier": multiplier}
