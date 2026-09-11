import logging

logging.basicConfig(level=logging.ERROR)

def process_payment(request):
    amount = request["amount"]
    if "billing_address" in request:
        address = request["billing_address"]
    else:
        logging.error("Missing 'billing_address' in request. Please ensure that the request includes a valid 'billing_address'.")
        raise ValueError("The 'billing_address' key is required for payment processing. Please check the request and try again.")

    return {
        "amount": amount,
        "address": address
    }