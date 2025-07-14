import json

# Check what was extracted from B787
try:
    with open('B787MMEL.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f'Total items extracted: {len(data)}')
    for i, item in enumerate(data):
        print(f'{i+1}. {item["itemNumber"]} - {item["title"]} (ATA {item["ataChapter"]})')
        print(f'   Category: {item["deferralCategory"]}, Qty: {item["quantityInstalled"]}/{item["quantityRequired"]}')
        print(f'   Remarks: {item["remarks"]["summary"][:100]}...')
        print()
except FileNotFoundError:
    print("B787MMEL.json not found")
except Exception as e:
    print(f"Error reading B787MMEL.json: {e}")
