from app.tools.repository import list_files, read_file, search_code


print("=== FILES ===")
print(list_files())

print("\n=== PAYMENT.PY ===")
print(read_file("demo/sample_repo/app/services/payment.py"))

print("\n=== SEARCH ===")
print(search_code("billing_address"))