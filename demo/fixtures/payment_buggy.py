def process_payment(request):
    amount = request["amount"]
    address = request["billing_address"]

    return {
        "amount": amount,
        "address": address
    }