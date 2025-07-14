import json
from collections import defaultdict, Counter

def analyze_a380_mmel():
    """Comprehensive analysis of A380 MMEL parsing results"""
    
    # Load the A380 MMEL data
    with open('A380MMEL_v2.json', 'r', encoding='utf-8') as f:
        a380_items = json.load(f)
    
    print("=== A380 MMEL PARSING ANALYSIS ===")
    print(f"Total items parsed: {len(a380_items)}")
    print()
    
    # ATA Chapter analysis
    ata_chapters = defaultdict(int)
    for item in a380_items:
        ata_chapters[item['ataChapter']] += 1
    
    print("ATA Chapter distribution:")
    for chapter in sorted(ata_chapters.keys()):
        print(f"  ATA {chapter}: {ata_chapters[chapter]} items")
    print(f"Total ATA chapters: {len(ata_chapters)}")
    print()
    
    # Deferral category analysis
    categories = Counter(item['deferralCategory'] for item in a380_items)
    print("Deferral Categories:")
    for cat, count in categories.most_common():
        if cat:
            print(f"  Category {cat}: {count} items")
        else:
            print(f"  Empty category: {count} items")
    print()
    
    # Quantity analysis
    has_quantities = sum(1 for item in a380_items if item['quantityInstalled'] > 0 or item['quantityRequired'] > 0)
    zero_quantities = sum(1 for item in a380_items if item['quantityInstalled'] == 0 and item['quantityRequired'] == 0)
    
    print("Quantity Analysis:")
    print(f"  Items with quantities: {has_quantities}")
    print(f"  Items with zero quantities: {zero_quantities}")
    print()
    
    # Procedures analysis
    items_with_maint = sum(1 for item in a380_items if item['maintenanceProcedures'])
    items_with_ops = sum(1 for item in a380_items if item['operationalProcedures'])
    items_with_remarks = sum(1 for item in a380_items if item['remarks']['summary'])
    items_with_steps = sum(1 for item in a380_items if item['remarks']['steps'])
    
    print("Procedures Analysis:")
    print(f"  Items with maintenance procedures: {items_with_maint}")
    print(f"  Items with operational procedures: {items_with_ops}")
    print(f"  Items with remarks: {items_with_remarks}")
    print(f"  Items with bullet-point steps: {items_with_steps}")
    print()
    
    # Sample some items with different characteristics
    print("Sample Items:")
    
    # Find item with procedures
    for item in a380_items:
        if item['maintenanceProcedures'] and item['operationalProcedures']:
            print(f"\nItem with both procedures: {item['itemNumber']} - {item['title']}")
            print(f"  Category: {item['deferralCategory']}")
            print(f"  Quantities: {item['quantityInstalled']}/{item['quantityRequired']}")
            print(f"  Maintenance: {item['maintenanceProcedures'][:1]}")
            print(f"  Operations: {item['operationalProcedures'][:1]}")
            break
    
    # Find item with remarks
    for item in a380_items:
        if item['remarks']['summary'] and len(item['remarks']['summary']) > 50:
            print(f"\nItem with detailed remarks: {item['itemNumber']} - {item['title']}")
            print(f"  Category: {item['deferralCategory']}")
            print(f"  Remarks: {item['remarks']['summary'][:100]}...")
            break
    
    # Quality checks
    print("\n=== QUALITY CHECKS ===")
    
    # Check for empty categories
    empty_categories = sum(1 for item in a380_items if not item['deferralCategory'])
    print(f"Items with empty deferral categories: {empty_categories}")
    
    # Check for unusually long titles
    long_titles = [item for item in a380_items if len(item['title']) > 80]
    print(f"Items with long titles (>80 chars): {len(long_titles)}")
    if long_titles:
        print(f"  Example: {long_titles[0]['itemNumber']} - {long_titles[0]['title'][:60]}...")
    
    # Check for items with high quantities
    high_qty_items = [item for item in a380_items if item['quantityInstalled'] > 10]
    print(f"Items with high quantities (>10): {len(high_qty_items)}")
    if high_qty_items:
        print(f"  Example: {high_qty_items[0]['itemNumber']} - {high_qty_items[0]['title'][:50]}... (Qty: {high_qty_items[0]['quantityInstalled']}/{high_qty_items[0]['quantityRequired']})")
    
    # Check format consistency
    item_number_formats = defaultdict(int)
    for item in a380_items:
        parts = item['itemNumber'].split('-')
        if len(parts) >= 3:
            format_type = f"{len(parts[0])}-{len(parts[1])}-{len(parts[2])}"
            item_number_formats[format_type] += 1
    
    print(f"\nItem number formats:")
    for fmt, count in item_number_formats.items():
        print(f"  {fmt}: {count} items")
    
    print(f"\n=== AIRCRAFT TYPE COMPARISON ===")
    
    # Load other aircraft for comparison
    aircraft_counts = {}
    try:
        with open('A320MMEL.json', 'r', encoding='utf-8') as f:
            aircraft_counts['A320'] = len(json.load(f))
    except FileNotFoundError:
        pass
    
    try:
        with open('A350MMEL.json', 'r', encoding='utf-8') as f:
            aircraft_counts['A350'] = len(json.load(f))
    except FileNotFoundError:
        pass
    
    try:
        with open('B787MMEL.json', 'r', encoding='utf-8') as f:
            aircraft_counts['B787'] = len(json.load(f))
    except FileNotFoundError:
        pass
    
    aircraft_counts['A380'] = len(a380_items)
    
    print("Aircraft MMEL item counts:")
    for aircraft, count in sorted(aircraft_counts.items()):
        print(f"  {aircraft}: {count:,} items")
    
    # Show comparisons
    if 'A320' in aircraft_counts:
        diff = aircraft_counts['A380'] - aircraft_counts['A320']
        pct = (diff / aircraft_counts['A320'] * 100)
        print(f"\nA380 vs A320: {diff:+d} items ({pct:+.1f}%)")
    
    if 'A350' in aircraft_counts:
        diff = aircraft_counts['A380'] - aircraft_counts['A350']
        pct = (diff / aircraft_counts['A350'] * 100)
        print(f"A380 vs A350: {diff:+d} items ({pct:+.1f}%)")
    
    if 'B787' in aircraft_counts:
        diff = aircraft_counts['A380'] - aircraft_counts['B787']
        pct = (diff / aircraft_counts['B787'] * 100)
        print(f"A380 vs B787: {diff:+d} items ({pct:+.1f}%)")

if __name__ == "__main__":
    analyze_a380_mmel()
