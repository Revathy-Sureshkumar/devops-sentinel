def process_payment(request):
    amount = request["amount"]
    if 'billing_address' in request:
        address = request["billing_address"]
    else:
        raise ValueError("Missing 'billing_address' in the request")

    return {
        "amount": amount,
        "address": address
    }