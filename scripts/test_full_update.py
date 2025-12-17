import os
import sys
import json
import uuid
import requests

BASE_URL = os.environ.get("ASIRIA_API", "http://localhost:8080")
USERNAME = os.environ.get("ASIRIA_USER", "0712345678")
PASSWORD = os.environ.get("ASIRIA_PASS", "game")

def get_token():
    r = requests.post(f"{BASE_URL}/api/token/", json={"phone_number": USERNAME, "password": PASSWORD})
    try:
        r.raise_for_status()
    except requests.HTTPError:
        print("Login failed:", r.status_code, r.text)
        raise
    return r.json()["access"]

def auth_headers(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def pick_first_id(url, token, key="results"):
    r = requests.get(f"{BASE_URL}{url}", headers=auth_headers(token))
    r.raise_for_status()
    data = r.json()
    if isinstance(data, list):
        return data[0]
    if key in data and isinstance(data[key], list) and data[key]:
        return data[key][0]
    # Fallback when simple list is returned
    if isinstance(data, dict):
        # try to find an id in first value
        for v in data.values():
            if isinstance(v, list) and v:
                return v[0]
    raise RuntimeError(f"No item found from {url}: {data}")


def ensure_po(token):
    # Create a minimal PO via the create endpoint
    supplier = pick_first_id("/api/suppliers/", token)
    product = pick_first_id("/api/products/", token)
    unit = pick_first_id("/api/units/", token)
    payload = {
        "supplier_id": supplier.get("supplier_id") or supplier.get("id"),
        "notes": "Test PO",
        "items": [
            {
                "product_id": product.get("product_id") or product.get("id"),
                "unit_id": unit.get("unit_id") or unit.get("id"),
                "quantity": 2,
                "price_per_unit": "100.00"
            }
        ]
    }
    r = requests.post(f"{BASE_URL}/api/purchase-orders/create/", headers=auth_headers(token), data=json.dumps(payload))
    r.raise_for_status()
    return r.json()["po_header_id"]


def test_po_full_update(token, po_id):
    # Fetch full before
    r = requests.get(f"{BASE_URL}/api/purchase-orders/{po_id}/full/", headers=auth_headers(token))
    r.raise_for_status()
    full = r.json()
    details = full.get("details", [])
    first_detail_id = details[0]["po_detail_id"] if details else None

    update_payload = {
        "expected_date": "2025-12-31",
        "notes": "Updated via script",
        "details": [
            {
                "po_detail_id": first_detail_id,
                "quantity": 5,
                "price_per_unit": "120.00"
            },
            {
                # create a new line (reuse same product/unit ids from existing)
                "product_id": details[0]["product"],
                "unit_id": details[0]["unit"],
                "quantity": 1,
                "price_per_unit": "90.00"
            }
        ]
    }
    r = requests.put(f"{BASE_URL}/api/purchase-orders/{po_id}/full/", headers=auth_headers(token), data=json.dumps(update_payload))
    r.raise_for_status()
    updated = r.json()
    print("PO updated. Details count:", len(updated.get("details", [])))


def ensure_purchase(token, po_id):
    # Convert PO to Purchase
    r = requests.post(f"{BASE_URL}/api/purchase-orders/{po_id}/convert-to-purchase/", headers=auth_headers(token), data=json.dumps({}))
    if r.status_code == 409:
        purchase_id = r.json().get("purchase_header_id")
    else:
        r.raise_for_status()
        purchase_id = r.json()["purchase_header_id"]
    return purchase_id


def test_purchase_full_update(token, purchase_id):
    # Fetch full before
    r = requests.get(f"{BASE_URL}/api/purchases/{purchase_id}/full/", headers=auth_headers(token))
    r.raise_for_status()
    full = r.json()
    details = full.get("details", [])
    first_detail_id = details[0]["purchase_detail_id"] if details else None

    update_payload = {
        "invoice_number": "INV-SCRIPT-UPDATED",
        "details": [
            {
                "purchase_detail_id": first_detail_id,
                "quantity": 9,
                "price_per_unit": "110.00",
                "discount": "5.00"
            }
        ]
    }
    r = requests.put(f"{BASE_URL}/api/purchases/{purchase_id}/full/", headers=auth_headers(token), data=json.dumps(update_payload))
    r.raise_for_status()
    updated = r.json()
    print("Purchase updated. Subtotal:", updated.get("subtotal"))


if __name__ == "__main__":
    token = get_token()
    po_id = ensure_po(token)
    test_po_full_update(token, po_id)
    purchase_id = ensure_purchase(token, po_id)
    test_purchase_full_update(token, purchase_id)
    print("All tests passed.")
