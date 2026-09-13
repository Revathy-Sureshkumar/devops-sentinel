def process_payment(request):
    if "amount" not in request or "billing_address" not in request:
        raise ValueError("Request must include 'amount' and 'billing_address' keys")
    
    amount = request["amount"]
    address = request["billing_address"]

    return {
        "amount": amount,
        "address": address
    }