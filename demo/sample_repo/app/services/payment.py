def process_payment(request):
    if "billing_address" not in request:
        raise ValueError("Missing 'billing_address' in the request")
    amount = request["amount"]
    address = request["billing_address"]

    return {
        "amount": amount,
        "address": address
    }