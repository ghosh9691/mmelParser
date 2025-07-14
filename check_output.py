import json

# Load and examine the generated JSON with proper encoding
with open('A320MMEL.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f'Total items: {len(data)}')
print('\nFirst few items:')
for i, item in enumerate(data[:5]):
    print(f'{i+1}. {item["itemNumber"]} - {item["title"]} (ATA {item["ataChapter"]})')
    print(f'   Category: {item["deferralCategory"]}, Qty: {item["quantityInstalled"]}/{item["quantityRequired"]}')
    print(f'   Remarks: {item["remarks"]["summary"][:100]}...')
    print()

print('\nSample full item:')
print(json.dumps(data[0], indent=2))
