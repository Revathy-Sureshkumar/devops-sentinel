def process_payment(request):
    if "amount" not in request or "billing_address" not in request:
        raise ValueError("Request is missing required fields: amount and billing_address")
    
    amount = request["amount"]
    address = request["billing_address"]

    return {
        "amount": amount,
        "address": address
    }