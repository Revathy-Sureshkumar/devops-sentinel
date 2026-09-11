def process_payment(request):
    if "amount" not in request:
        raise ValueError("Missing required field 'amount' in request")
    if "billing_address" not in request:
        raise ValueError("Missing required field 'billing_address' in request. Please ensure the request includes a billing address.")
    
    amount = request["amount"]
    address = request["billing_address"]

    return {
        "amount": amount,
        "address": address
    }