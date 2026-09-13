def process_payment(request):
    amount = request["amount"]
    if "billing_address" in request:
        address = request["billing_address"]
    else:
        # Raise ValueError when the "billing_address" key is missing
        raise ValueError("Missing billing_address in request")

    return {
        "amount": amount,
        "address": address
    }