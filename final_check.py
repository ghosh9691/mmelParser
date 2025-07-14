import json

# Load and examine the generated JSON
with open('A320MMEL.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f'Total items: {len(data)}')

# Check distribution by ATA chapters
ata_chapters = {}
for item in data:
    ata = item["ataChapter"]
    if ata not in ata_chapters:
        ata_chapters[ata] = 0
    ata_chapters[ata] += 1

print(f'\nATA Chapter distribution:')
for ata in sorted(ata_chapters.keys()):
    print(f'  ATA {ata}: {ata_chapters[ata]} items')

# Check category distribution
categories = {}
for item in data:
    cat = item["deferralCategory"]
    if cat not in categories:
        categories[cat] = 0
    categories[cat] += 1

print(f'\nDeferral Category distribution:')
for cat in sorted(categories.keys()):
    print(f'  Category {cat}: {categories[cat]} items')

# Show some sample items from different ATA chapters
print(f'\nSample items from different ATA chapters:')
sample_atas = ["21", "22", "23", "24", "25"]
for ata in sample_atas:
    for item in data:
        if item["ataChapter"] == ata:
            print(f'  ATA {ata}: {item["itemNumber"]} - {item["title"][:50]}... (Qty: {item["quantityInstalled"]}/{item["quantityRequired"]})')
            break

# Check for items with maintenance and operational procedures
has_maintenance = 0
has_operational = 0
for item in data:
    if item["maintenanceProcedures"]:
        has_maintenance += 1
    if item["operationalProcedures"]:
        has_operational += 1

print(f'\nProcedures:')
print(f'  Items with maintenance procedures: {has_maintenance}')
print(f'  Items with operational procedures: {has_operational}')

# Check for items with bullet points
has_steps = 0
for item in data:
    if item["remarks"]["steps"]:
        has_steps += 1

print(f'  Items with bullet-point steps: {has_steps}')
