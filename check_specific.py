import json

# Load and find a normal MMEL item
with open('A320MMEL.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find the 21-21-01 item specifically
for item in data:
    if item["itemNumber"] == "21-21-01":
        print("21-21-01 item:")
        print(json.dumps(item, indent=2))
        break

# Look at a few more items to see patterns
print("\nOther items:")
for i, item in enumerate(data[1:6]):
    print(f"{i+2}. {item['itemNumber']} - Qty: {item['quantityInstalled']}/{item['quantityRequired']} - Cat: {item['deferralCategory']}")
