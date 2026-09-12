def process_payment(request):
    if "amount" not in request:
        raise ValueError("Missing 'amount' in the request")
    if "billing_address" not in request:
        raise ValueError("Missing 'billing_address' in the request")
    
    amount = request["amount"]
    address = request.get("billing_address", None)  # Preserve the original address if present
    
    return {
        "amount": amount,
        "address": address
    }