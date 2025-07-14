import json

# Load and analyze the B787 JSON
with open('B787MMEL.json', 'r', encoding='utf-8') as f:
    b787_data = json.load(f)

print(f'=== Boeing 787 MMEL Analysis ===')
print(f'Total items: {len(b787_data)}')

# Check distribution by ATA chapters
ata_chapters = {}
for item in b787_data:
    ata = item["ataChapter"]
    if ata not in ata_chapters:
        ata_chapters[ata] = 0
    ata_chapters[ata] += 1

print(f'\nATA Chapter distribution:')
for ata in sorted(ata_chapters.keys()):
    print(f'  ATA {ata}: {ata_chapters[ata]} items')

# Check category distribution
categories = {}
for item in b787_data:
    cat = item["deferralCategory"]
    if cat not in categories:
        categories[cat] = 0
    categories[cat] += 1

print(f'\nDeferral Category distribution:')
for cat in sorted(categories.keys()):
    print(f'  Category {cat}: {categories[cat]} items')

# Show some sample items from different ATA chapters
print(f'\nSample items from different ATA chapters:')
sample_atas = ["21", "34", "52", "73", "78"]
for ata in sample_atas:
    for item in b787_data:
        if item["ataChapter"] == ata:
            print(f'  ATA {ata}: {item["itemNumber"]} - {item["title"][:50]}... (Qty: {item["quantityInstalled"]}/{item["quantityRequired"]})')
            break

# Check for items with maintenance and operational procedures
has_maintenance = 0
has_operational = 0
for item in b787_data:
    if item["maintenanceProcedures"]:
        has_maintenance += 1
    if item["operationalProcedures"]:
        has_operational += 1

print(f'\nProcedures:')
print(f'  Items with maintenance procedures: {has_maintenance}')
print(f'  Items with operational procedures: {has_operational}')

# Check for items with bullet points
has_steps = 0
for item in b787_data:
    if item["remarks"]["steps"]:
        has_steps += 1

print(f'  Items with bullet-point steps: {has_steps}')

# Compare with A320 data
try:
    with open('A320MMEL.json', 'r', encoding='utf-8') as f:
        a320_data = json.load(f)
    
    print(f'\n=== Comparison with Airbus A320 ===')
    print(f'A320 Total items: {len(a320_data)}')
    print(f'B787 Total items: {len(b787_data)}')
    print(f'Difference: {len(b787_data) - len(a320_data)} items ({((len(b787_data) - len(a320_data))/len(a320_data)*100):+.1f}%)')
    
except Exception as e:
    print(f'Could not compare with A320: {e}')

# Show some items with detailed structure
print(f'\nDetailed sample items:')
for i, item in enumerate(b787_data[:3]):
    print(f'\n{i+1}. {item["itemNumber"]} - {item["title"]}')
    print(f'   Category: {item["deferralCategory"]}, Qty: {item["quantityInstalled"]}/{item["quantityRequired"]}')
    if item["maintenanceProcedures"]:
        print(f'   Maintenance: {item["maintenanceProcedures"][:2]}...')
    if item["operationalProcedures"]:
        print(f'   Operational: {item["operationalProcedures"][:2]}...')
    if item["remarks"]["steps"]:
        print(f'   Steps: {item["remarks"]["steps"][:2]}...')
        
# Check for potential parsing issues
print(f'\n=== Quality Check ===')
empty_categories = sum(1 for item in b787_data if not item["deferralCategory"])
print(f'Items with empty categories: {empty_categories}')

zero_qty = sum(1 for item in b787_data if item["quantityInstalled"] == 0 and item["quantityRequired"] == 0)
print(f'Items with 0/0 quantities: {zero_qty}')

long_titles = sum(1 for item in b787_data if len(item["title"]) > 150)
print(f'Items with very long titles (>150 chars): {long_titles}')
