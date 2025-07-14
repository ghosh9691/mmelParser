import sqlite3

def demo_database_queries():
    """Demonstrate various useful queries for the enhanced MMEL database"""
    
    conn = sqlite3.connect('mmel_db.db')
    cursor = conn.cursor()
    
    print("🗃️  ENHANCED MMEL DATABASE QUERY EXAMPLES")
    print("=" * 60)
    
    # Query 1: Find all items for a specific aircraft and ATA chapter
    print("\n1️⃣  Items for A320 ATA Chapter 28 (Fuel):")
    cursor.execute('''
        SELECT item_number, sequence_number, title, deferral_category
        FROM mmel_items 
        WHERE aircraft_type = 'A320' AND ata_chapter = '28'
        ORDER BY item_number, sequence_number
        LIMIT 5
    ''')
    
    for item_num, seq, title, category in cursor.fetchall():
        print(f"  {item_num} (seq {seq}) - {category}: {title[:50]}...")
    
    # Query 2: Find items with maintenance procedures
    print("\n2️⃣  Items with maintenance procedures (B787):")
    cursor.execute('''
        SELECT DISTINCT mi.item_number, mi.title, COUNT(mp.id) as proc_count
        FROM mmel_items mi
        JOIN maintenance_procedures mp ON mi.id = mp.mmel_item_id
        WHERE mi.aircraft_type = 'B787'
        GROUP BY mi.item_number, mi.title
        ORDER BY proc_count DESC
        LIMIT 5
    ''')
    
    for item_num, title, proc_count in cursor.fetchall():
        print(f"  {item_num}: {title[:40]}... ({proc_count} procedures)")
    
    # Query 3: Category A items across all aircraft
    print("\n3️⃣  Category A (critical) items by aircraft:")
    cursor.execute('''
        SELECT aircraft_type, COUNT(*) as category_a_count
        FROM mmel_items 
        WHERE deferral_category = 'A'
        GROUP BY aircraft_type
        ORDER BY category_a_count DESC
    ''')
    
    for aircraft, count in cursor.fetchall():
        print(f"  {aircraft}: {count} Category A items")
    
    # Query 4: Items with most duplicates (different configurations)
    print("\n4️⃣  Items with most configuration variations:")
    cursor.execute('''
        SELECT aircraft_type, item_number, COUNT(*) as variations, 
               MAX(title) as sample_title
        FROM mmel_items 
        GROUP BY aircraft_type, item_number
        HAVING COUNT(*) > 5
        ORDER BY variations DESC
        LIMIT 5
    ''')
    
    for aircraft, item_num, variations, title in cursor.fetchall():
        print(f"  {aircraft} - {item_num}: {variations} variations")
        print(f"    Sample: {title[:60]}...")
    
    # Query 5: Search for specific terms across all items
    print("\n5️⃣  Search for 'autopilot' related items:")
    cursor.execute('''
        SELECT aircraft_type, item_number, title
        FROM mmel_items 
        WHERE title LIKE '%autopilot%' OR title LIKE '%AUTOPILOT%'
        LIMIT 5
    ''')
    
    for aircraft, item_num, title in cursor.fetchall():
        print(f"  {aircraft} - {item_num}: {title[:50]}...")
    
    # Query 6: Items with operational procedures
    print("\n6️⃣  Items with operational procedures (A350):")
    cursor.execute('''
        SELECT mi.item_number, mi.title, 
               GROUP_CONCAT(op.procedure_text, ' | ') as procedures
        FROM mmel_items mi
        JOIN operational_procedures op ON mi.id = op.mmel_item_id
        WHERE mi.aircraft_type = 'A350'
        GROUP BY mi.item_number, mi.title
        HAVING COUNT(op.id) > 1
        LIMIT 3
    ''')
    
    for item_num, title, procedures in cursor.fetchall():
        print(f"  {item_num}: {title[:40]}...")
        print(f"    Procedures: {procedures[:80]}...")
    
    # Query 7: Summary statistics
    print("\n7️⃣  Database summary statistics:")
    cursor.execute('''
        SELECT 
            COUNT(*) as total_items,
            COUNT(DISTINCT CONCAT(aircraft_type, '|', item_number)) as unique_items,
            COUNT(DISTINCT aircraft_type) as aircraft_types,
            COUNT(DISTINCT ata_chapter) as ata_chapters
        FROM mmel_items
    ''')
    
    total, unique, aircraft_count, ata_count = cursor.fetchone()
    print(f"  Total items: {total:,}")
    print(f"  Unique items: {unique:,}")
    print(f"  Aircraft types: {aircraft_count}")
    print(f"  ATA chapters: {ata_count}")
    
    conn.close()
    
    print(f"\n✅ Query demonstration complete!")
    print(f"💡 Use sequence_number to distinguish between duplicate item numbers")
    print(f"🔗 Join with maintenance_procedures, operational_procedures, and remarks_steps for detailed info")

if __name__ == "__main__":
    demo_database_queries()
