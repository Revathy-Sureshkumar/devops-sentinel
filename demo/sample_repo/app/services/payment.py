def process_payment(request):
    amount = request["amount"]
    if "billing_address" not in request:
        raise ValueError("billing_address is required")
    address = request["billing_address"]

    return {
        "amount": amount,
        "address": address
    }