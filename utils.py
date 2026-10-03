import numpy as np
from twilio.rest import Client

POLICY_LIMITS = {
    "Food": 1500,
    "Travel": 5000,
    "Office Supplies": 3000,
    "Software": 10000,
    "Healthcare": 5000,
    "Entertainment": 2000
}


def check_policy(category, amount):

    limit = POLICY_LIMITS.get(category)

    if limit is None:
        return {
            "status": "REVIEW",
            "message": "No policy limit configured for this category."
        }

    if amount > limit:

        excess = amount - limit

        return {
            "status": "VIOLATION",
            "limit": limit,
            "excess": excess,
            "message": f"Amount exceeds policy limit by ₹{excess:.2f}"
        }

    return {
        "status": "PASS",
        "limit": limit,
        "excess": 0,
        "message": "Expense is within policy."
    }


def detect_anomaly(current_amount, previous_amounts):

    if not previous_amounts:
        return {
            "is_anomaly": False,
            "average": 0,
            "message": "No historical data available."
        }

    average = np.mean(previous_amounts)
    std = np.std(previous_amounts)

    if std == 0:
        is_anomaly = current_amount > average * 2
    else:
        is_anomaly = current_amount > average + (2 * std)

    if is_anomaly:
        message = (
            f"Current expense ₹{current_amount:.2f} "
            f"is unusually high compared with the historical average "
            f"of ₹{average:.2f}."
        )
    else:
        message = "Expense is within the normal historical range."

    return {
        "is_anomaly": is_anomaly,
        "average": average,
        "message": message
    }

def check_duplicate(invoice, previous_invoices):

    for old_invoice in previous_invoices:

        same_number = (
            invoice.get("invoice_number")
            and invoice.get("invoice_number")
            == old_invoice.get("invoice_number")
        )

        same_vendor = (
            invoice.get("vendor")
            and invoice.get("vendor")
            == old_invoice.get("vendor")
        )

        same_amount = (
            invoice.get("total")
            == old_invoice.get("total")
        )

        if same_number and same_vendor and same_amount:

            return {
                "is_duplicate": True,
                "message": (
                    f"Possible duplicate of invoice "
                    f"{old_invoice.get('invoice_number')}."
                )
            }

    return {
        "is_duplicate": False,
        "message": "No duplicate detected."
    }

def generate_final_status(
    policy_result,
    anomaly_result,
    duplicate_result
):

    issues = []

    if policy_result["status"] == "VIOLATION":
        issues.append("Policy violation")

    if anomaly_result["is_anomaly"]:
        issues.append("Unusual amount")

    if duplicate_result["is_duplicate"]:
        issues.append("Possible duplicate")

    if issues:

        return {
            "status": "REQUIRES REVIEW",
            "issues": issues
        }

    return {
        "status": "APPROVED FOR PROCESSING",
        "issues": []
    }


from twilio.rest import Client
import json


def send_whatsapp_message(
    account_sid,
    auth_token,
    from_number,
    to_number,
    content_sid,
    variables
):

    client = Client(
        account_sid,
        auth_token
    )

    whatsapp_message = client.messages.create(
        from_=from_number,
        to=to_number,
        content_sid=content_sid,
        content_variables=json.dumps(variables)
    )

    return whatsapp_message.sid