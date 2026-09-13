def process_payment(request):
    amount = request["amount"]
    
    if "billing_address" not in request:
        raise ValueError("Missing 'billing_address' in request")
    
    address = request["billing_address"]

    return {
        "amount": amount,
        "address": address
    }