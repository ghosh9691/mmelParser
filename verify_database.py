import sqlite3
import json

def verify_database():
    """Verify the database contents and compare with JSON files"""
    
    conn = sqlite3.connect('mmel_database.db')
    cursor = conn.cursor()
    
    print("=== DATABASE VERIFICATION ===")
    
    # Check total items in database
    cursor.execute('SELECT COUNT(*) FROM mmel_items')
    total_db_items = cursor.fetchone()[0]
    print(f"Total items in database: {total_db_items:,}")
    
    # Check individual aircraft
    cursor.execute('SELECT aircraft_type, COUNT(*) FROM mmel_items GROUP BY aircraft_type ORDER BY aircraft_type')
    db_counts = cursor.fetchall()
    
    print("\nDatabase vs JSON file comparison:")
    print("Aircraft | DB Items | JSON Items | Status")
    print("-" * 45)
    
    json_files = {
        'A320': 'A320MMEL.json',
        'A330': 'A330MMEL.json', 
        'A350': 'A350MMEL.json',
        'A380': 'A380MMEL.json',
        'B38M': 'B38MMMEL.json',
        'B737': 'B737MMEL.json',
        'B748': 'B748MMEL.json',
        'B74F': 'B74FMMEL.json',
        'B767': 'B767MMEL.json',
        'B777': 'B777MMEL.json',
        'B787': 'B787MMEL.json'
    }
    
    total_json_items = 0
    
    for aircraft, db_count in db_counts:
        if aircraft in json_files:
            json_file = json_files[aircraft]
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                    json_count = len(json_data)
                    total_json_items += json_count
                    
                    status = "✅" if db_count == json_count else "❌"
                    print(f"{aircraft:>8} | {db_count:>8} | {json_count:>10} | {status}")
                    
                    if db_count != json_count:
                        print(f"  ⚠️  Mismatch: {db_count - json_count:+d} items")
                        
            except Exception as e:
                print(f"{aircraft:>8} | {db_count:>8} | ERROR     | ❌")
                print(f"  Error: {e}")
        else:
            print(f"{aircraft:>8} | {db_count:>8} | UNKNOWN   | ❓")
    
    print(f"\nTotal JSON items: {total_json_items:,}")
    print(f"Total DB items: {total_db_items:,}")
    print(f"Difference: {total_db_items - total_json_items:+d}")
    
    # Check for duplicate items
    cursor.execute('''
        SELECT aircraft_type, item_number, COUNT(*) as count 
        FROM mmel_items 
        GROUP BY aircraft_type, item_number 
        HAVING COUNT(*) > 1
        ORDER BY count DESC
    ''')
    
    duplicates = cursor.fetchall()
    if duplicates:
        print(f"\n⚠️  Found {len(duplicates)} duplicate items:")
        for dup in duplicates[:10]:  # Show first 10
            print(f"  {dup[0]} - {dup[1]} (appears {dup[2]} times)")
    else:
        print("\n✅ No duplicate items found")
    
    # Check aircraft with most items
    print("\n🏆 Aircraft with most MMEL items:")
    cursor.execute('SELECT aircraft_type, COUNT(*) as count FROM mmel_items GROUP BY aircraft_type ORDER BY count DESC LIMIT 5')
    top_aircraft = cursor.fetchall()
    
    for i, (aircraft, count) in enumerate(top_aircraft, 1):
        print(f"  {i}. {aircraft}: {count:,} items")
    
    # Check ATA chapters
    print("\n📊 ATA Chapter distribution:")
    cursor.execute('SELECT ata_chapter, COUNT(*) as count FROM mmel_items GROUP BY ata_chapter ORDER BY count DESC LIMIT 10')
    top_chapters = cursor.fetchall()
    
    for chapter, count in top_chapters:
        print(f"  ATA {chapter}: {count:,} items")
    
    # Sample some data
    print("\n🔍 Sample MMEL items:")
    cursor.execute('SELECT aircraft_type, item_number, title FROM mmel_items LIMIT 5')
    samples = cursor.fetchall()
    
    for aircraft, item_num, title in samples:
        print(f"  {aircraft} - {item_num}: {title[:50]}...")
    
    conn.close()

if __name__ == "__main__":
    verify_database()
