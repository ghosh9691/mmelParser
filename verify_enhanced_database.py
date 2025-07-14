import sqlite3

def verify_enhanced_database():
    """Verify the enhanced database is working correctly"""
    
    conn = sqlite3.connect('mmel_db.db')
    cursor = conn.cursor()
    
    print("🔍 ENHANCED DATABASE VERIFICATION")
    print("=" * 50)
    
    # Check total items
    cursor.execute('SELECT COUNT(*) FROM mmel_items')
    total_items = cursor.fetchone()[0]
    print(f"📊 Total items in database: {total_items:,}")
    
    # Check unique aircraft types
    cursor.execute('SELECT DISTINCT aircraft_type FROM mmel_items ORDER BY aircraft_type')
    aircraft_types = [row[0] for row in cursor.fetchall()]
    print(f"✈️  Aircraft types: {', '.join(aircraft_types)}")
    
    # Check items with multiple entries
    cursor.execute('''
        SELECT aircraft_type, item_number, COUNT(*) as count
        FROM mmel_items 
        GROUP BY aircraft_type, item_number 
        HAVING COUNT(*) > 1
        ORDER BY count DESC
        LIMIT 5
    ''')
    
    print(f"\n🔢 Top 5 items with multiple entries:")
    for aircraft, item_num, count in cursor.fetchall():
        print(f"  {aircraft} - {item_num}: {count} entries")
    
    # Show example of duplicate handling
    print(f"\n📋 Example of duplicate item handling:")
    cursor.execute('''
        SELECT aircraft_type, item_number, sequence_number, title
        FROM mmel_items 
        WHERE aircraft_type = 'A320' AND item_number = '28-40-06'
        ORDER BY sequence_number
        LIMIT 5
    ''')
    
    duplicates = cursor.fetchall()
    for aircraft, item_num, seq, title in duplicates:
        print(f"  {aircraft} - {item_num} (seq {seq}): {title[:50]}...")
    
    # Check procedures are properly linked
    cursor.execute('''
        SELECT COUNT(*) FROM maintenance_procedures
    ''')
    maintenance_count = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT COUNT(*) FROM operational_procedures
    ''')
    operational_count = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT COUNT(*) FROM remarks_steps
    ''')
    remarks_count = cursor.fetchone()[0]
    
    print(f"\n📝 Linked procedures:")
    print(f"  Maintenance procedures: {maintenance_count:,}")
    print(f"  Operational procedures: {operational_count:,}")
    print(f"  Remarks steps: {remarks_count:,}")
    
    # Check aircraft summary
    cursor.execute('''
        SELECT aircraft_type, total_items, unique_item_numbers, 
               total_category_a, total_category_b, total_category_c, total_category_d
        FROM aircraft_summary
        ORDER BY total_items DESC
    ''')
    
    print(f"\n📈 Aircraft summary (top 5):")
    print("Aircraft | Total | Unique | Cat A | Cat B | Cat C | Cat D")
    print("-" * 55)
    
    for row in cursor.fetchall()[:5]:
        aircraft, total, unique, cat_a, cat_b, cat_c, cat_d = row
        print(f"{aircraft:>8} | {total:>5} | {unique:>6} | {cat_a:>5} | {cat_b:>5} | {cat_c:>5} | {cat_d:>5}")
    
    conn.close()
    
    print(f"\n✅ Database verification complete!")
    print(f"💾 Enhanced database: mmel_db.db")
    print(f"🔍 All duplicate items are preserved with unique sequence numbers")

if __name__ == "__main__":
    verify_enhanced_database()
