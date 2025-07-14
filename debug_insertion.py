import sqlite3
import json

def debug_insertion_issues():
    """Debug why items are missing from database"""
    
    # Check A320 specifically
    print("=== DEBUGGING A320 INSERTION ===")
    
    with open('A320MMEL.json', 'r', encoding='utf-8') as f:
        a320_data = json.load(f)
    
    print(f"A320 JSON items: {len(a320_data)}")
    
    # Check for duplicate item numbers
    item_numbers = {}
    for item in a320_data:
        item_num = item.get('itemNumber', '')
        if item_num in item_numbers:
            item_numbers[item_num] += 1
        else:
            item_numbers[item_num] = 1
    
    duplicates = {k: v for k, v in item_numbers.items() if v > 1}
    print(f"Duplicate item numbers: {len(duplicates)}")
    
    if duplicates:
        print("Top duplicates:")
        for item_num, count in sorted(duplicates.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {item_num}: {count} times")
    
    # Check for empty item numbers
    empty_items = [item for item in a320_data if not item.get('itemNumber', '').strip()]
    print(f"Items with empty item numbers: {len(empty_items)}")
    
    # Check database
    conn = sqlite3.connect('mmel_database.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM mmel_items WHERE aircraft_type = "A320"')
    db_count = cursor.fetchone()[0]
    print(f"A320 DB items: {db_count}")
    
    # Check for specific duplicates in database
    cursor.execute('''
        SELECT item_number, COUNT(*) as count 
        FROM mmel_items 
        WHERE aircraft_type = "A320"
        GROUP BY item_number 
        HAVING COUNT(*) > 1
        ORDER BY count DESC
    ''')
    
    db_duplicates = cursor.fetchall()
    print(f"Database duplicates for A320: {len(db_duplicates)}")
    
    if db_duplicates:
        print("Database duplicates:")
        for item_num, count in db_duplicates[:5]:
            print(f"  {item_num}: {count} times")
    
    conn.close()
    
    # Calculate expected vs actual
    expected_unique = len(a320_data) - sum(v - 1 for v in duplicates.values())
    print(f"Expected unique items: {expected_unique}")
    print(f"Actual DB items: {db_count}")
    print(f"Difference: {db_count - expected_unique}")

if __name__ == "__main__":
    debug_insertion_issues()
