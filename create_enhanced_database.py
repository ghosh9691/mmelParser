import sqlite3
import json
import os
from datetime import datetime

def create_enhanced_mmel_database():
    """Create enhanced SQLite database that preserves all MMEL entries including duplicates"""
    
    # Create database connection
    conn = sqlite3.connect('mmel_db.db')
    cursor = conn.cursor()
    
    # Create main MMEL items table with sequence number to handle duplicates
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mmel_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aircraft_type TEXT NOT NULL,
            ata_chapter TEXT NOT NULL,
            item_number TEXT NOT NULL,
            sequence_number INTEGER NOT NULL,
            title TEXT NOT NULL,
            deferral_category TEXT,
            quantity_installed INTEGER DEFAULT 0,
            quantity_required INTEGER DEFAULT 0,
            remarks_summary TEXT,
            source_file TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(aircraft_type, item_number, sequence_number)
        )
    ''')
    
    # Create maintenance procedures table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS maintenance_procedures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mmel_item_id INTEGER,
            procedure_text TEXT NOT NULL,
            sequence_order INTEGER,
            FOREIGN KEY (mmel_item_id) REFERENCES mmel_items (id)
        )
    ''')
    
    # Create operational procedures table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS operational_procedures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mmel_item_id INTEGER,
            procedure_text TEXT NOT NULL,
            sequence_order INTEGER,
            FOREIGN KEY (mmel_item_id) REFERENCES mmel_items (id)
        )
    ''')
    
    # Create remarks steps table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS remarks_steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mmel_item_id INTEGER,
            step_text TEXT NOT NULL,
            sequence_order INTEGER,
            FOREIGN KEY (mmel_item_id) REFERENCES mmel_items (id)
        )
    ''')
    
    # Create enhanced aircraft summary table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aircraft_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aircraft_type TEXT UNIQUE NOT NULL,
            total_items INTEGER,
            unique_item_numbers INTEGER,
            total_category_a INTEGER DEFAULT 0,
            total_category_b INTEGER DEFAULT 0,
            total_category_c INTEGER DEFAULT 0,
            total_category_d INTEGER DEFAULT 0,
            total_empty_category INTEGER DEFAULT 0,
            items_with_maintenance_procedures INTEGER DEFAULT 0,
            items_with_operational_procedures INTEGER DEFAULT 0,
            items_with_remarks INTEGER DEFAULT 0,
            source_file TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_aircraft_type ON mmel_items (aircraft_type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_ata_chapter ON mmel_items (ata_chapter)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_item_number ON mmel_items (item_number)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_deferral_category ON mmel_items (deferral_category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_aircraft_item ON mmel_items (aircraft_type, item_number)')
    
    conn.commit()
    return conn

def insert_enhanced_mmel_data(conn, json_file_path):
    """Insert MMEL data preserving all entries including duplicates"""
    
    cursor = conn.cursor()
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            mmel_data = json.load(f)
        
        print(f"Processing {json_file_path}: {len(mmel_data)} items")
        
        if not mmel_data:
            print(f"Warning: {json_file_path} is empty")
            return 0
        
        items_inserted = 0
        
        for item in mmel_data:
            try:
                aircraft_type = item.get('aircraftType', '')
                item_number = item.get('itemNumber', '')
                
                # Find the next sequence number for this aircraft_type and item_number
                cursor.execute('''
                    SELECT COALESCE(MAX(sequence_number), 0) + 1 
                    FROM mmel_items 
                    WHERE aircraft_type = ? AND item_number = ?
                ''', (aircraft_type, item_number))
                
                sequence_number = cursor.fetchone()[0]
                
                # Insert main MMEL item
                cursor.execute('''
                    INSERT INTO mmel_items (
                        aircraft_type, ata_chapter, item_number, sequence_number, title, 
                        deferral_category, quantity_installed, quantity_required, 
                        remarks_summary, source_file
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    aircraft_type,
                    item.get('ataChapter', ''),
                    item_number,
                    sequence_number,
                    item.get('title', ''),
                    item.get('deferralCategory', ''),
                    item.get('quantityInstalled', 0),
                    item.get('quantityRequired', 0),
                    item.get('remarks', {}).get('summary', ''),
                    json_file_path
                ))
                
                # Get the inserted item ID
                mmel_item_id = cursor.lastrowid
                
                # Insert maintenance procedures
                maintenance_procedures = item.get('maintenanceProcedures', [])
                for i, procedure in enumerate(maintenance_procedures):
                    cursor.execute('''
                        INSERT INTO maintenance_procedures (mmel_item_id, procedure_text, sequence_order)
                        VALUES (?, ?, ?)
                    ''', (mmel_item_id, procedure, i + 1))
                
                # Insert operational procedures
                operational_procedures = item.get('operationalProcedures', [])
                for i, procedure in enumerate(operational_procedures):
                    cursor.execute('''
                        INSERT INTO operational_procedures (mmel_item_id, procedure_text, sequence_order)
                        VALUES (?, ?, ?)
                    ''', (mmel_item_id, procedure, i + 1))
                
                # Insert remarks steps
                remarks_steps = item.get('remarks', {}).get('steps', [])
                for i, step in enumerate(remarks_steps):
                    cursor.execute('''
                        INSERT INTO remarks_steps (mmel_item_id, step_text, sequence_order)
                        VALUES (?, ?, ?)
                    ''', (mmel_item_id, step, i + 1))
                
                items_inserted += 1
                
            except Exception as e:
                print(f"Error inserting item {item.get('itemNumber', 'unknown')}: {e}")
                continue
        
        conn.commit()
        return items_inserted
        
    except Exception as e:
        print(f"Error processing {json_file_path}: {e}")
        return 0

def update_enhanced_aircraft_summary(conn):
    """Update enhanced aircraft summary statistics"""
    
    cursor = conn.cursor()
    
    # Get all aircraft types
    cursor.execute('SELECT DISTINCT aircraft_type FROM mmel_items')
    aircraft_types = [row[0] for row in cursor.fetchall()]
    
    for aircraft_type in aircraft_types:
        # Count total items
        cursor.execute('SELECT COUNT(*) FROM mmel_items WHERE aircraft_type = ?', (aircraft_type,))
        total_items = cursor.fetchone()[0]
        
        # Count unique item numbers
        cursor.execute('SELECT COUNT(DISTINCT item_number) FROM mmel_items WHERE aircraft_type = ?', (aircraft_type,))
        unique_items = cursor.fetchone()[0]
        
        # Count by category
        cursor.execute('SELECT COUNT(*) FROM mmel_items WHERE aircraft_type = ? AND deferral_category = ?', (aircraft_type, 'A'))
        category_a = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM mmel_items WHERE aircraft_type = ? AND deferral_category = ?', (aircraft_type, 'B'))
        category_b = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM mmel_items WHERE aircraft_type = ? AND deferral_category = ?', (aircraft_type, 'C'))
        category_c = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM mmel_items WHERE aircraft_type = ? AND deferral_category = ?', (aircraft_type, 'D'))
        category_d = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM mmel_items WHERE aircraft_type = ? AND (deferral_category = "" OR deferral_category IS NULL)', (aircraft_type,))
        empty_category = cursor.fetchone()[0]
        
        # Count items with procedures
        cursor.execute('SELECT COUNT(DISTINCT mmel_item_id) FROM maintenance_procedures mp JOIN mmel_items mi ON mp.mmel_item_id = mi.id WHERE mi.aircraft_type = ?', (aircraft_type,))
        items_with_maintenance = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT mmel_item_id) FROM operational_procedures op JOIN mmel_items mi ON op.mmel_item_id = mi.id WHERE mi.aircraft_type = ?', (aircraft_type,))
        items_with_operational = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM mmel_items WHERE aircraft_type = ? AND remarks_summary != ""', (aircraft_type,))
        items_with_remarks = cursor.fetchone()[0]
        
        # Get source file
        cursor.execute('SELECT source_file FROM mmel_items WHERE aircraft_type = ? LIMIT 1', (aircraft_type,))
        source_file = cursor.fetchone()[0]
        
        # Insert or update summary
        cursor.execute('''
            INSERT OR REPLACE INTO aircraft_summary (
                aircraft_type, total_items, unique_item_numbers, total_category_a, 
                total_category_b, total_category_c, total_category_d, total_empty_category,
                items_with_maintenance_procedures, items_with_operational_procedures,
                items_with_remarks, source_file, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            aircraft_type, total_items, unique_items, category_a, category_b, category_c, category_d,
            empty_category, items_with_maintenance, items_with_operational, items_with_remarks, source_file
        ))
    
    conn.commit()

def main():
    """Main function to process all MMEL JSON files with enhanced database"""
    
    # Find all MMEL JSON files
    json_files = [
        'A320MMEL.json',
        'A330MMEL.json', 
        'A350MMEL.json',
        'A380MMEL.json',
        'B38MMMEL.json',
        'B737MMEL.json',
        'B748MMEL.json',
        'B74FMMEL.json',
        'B767MMEL.json',
        'B777MMEL.json',
        'B787MMEL.json'
    ]
    
    # Create enhanced database
    print("Creating enhanced MMEL database...")
    conn = create_enhanced_mmel_database()
    
    total_items = 0
    processed_files = 0
    
    # Process each JSON file
    for json_file in json_files:
        if os.path.exists(json_file):
            items_count = insert_enhanced_mmel_data(conn, json_file)
            total_items += items_count
            processed_files += 1
            print(f"✅ {json_file}: {items_count} items inserted")
        else:
            print(f"❌ {json_file}: File not found")
    
    # Update aircraft summary statistics
    print("\nUpdating aircraft summary statistics...")
    update_enhanced_aircraft_summary(conn)
    
    # Display summary
    print(f"\n🎯 ENHANCED DATABASE CREATION COMPLETE!")
    print(f"📁 Processed files: {processed_files}")
    print(f"📊 Total MMEL items inserted: {total_items:,}")
    
    # Show aircraft summary
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM aircraft_summary ORDER BY aircraft_type')
    summaries = cursor.fetchall()
    
    print(f"\n📋 AIRCRAFT SUMMARY:")
    print("Aircraft | Total | Unique | Cat A | Cat B | Cat C | Cat D | Empty | Maint | Ops | Remarks")
    print("-" * 95)
    
    for summary in summaries:
        aircraft_type = summary[1]
        total = summary[2]
        unique = summary[3]
        cat_a = summary[4]
        cat_b = summary[5]
        cat_c = summary[6]
        cat_d = summary[7]
        empty = summary[8]
        maint = summary[9]
        ops = summary[10]
        remarks = summary[11]
        
        print(f"{aircraft_type:>8} | {total:>5} | {unique:>6} | {cat_a:>5} | {cat_b:>5} | {cat_c:>5} | {cat_d:>5} | {empty:>5} | {maint:>5} | {ops:>3} | {remarks:>7}")
    
    # Show duplicate statistics
    print(f"\n📊 DUPLICATE STATISTICS:")
    cursor.execute('''
        SELECT aircraft_type, item_number, COUNT(*) as count
        FROM mmel_items 
        GROUP BY aircraft_type, item_number 
        HAVING COUNT(*) > 1
        ORDER BY count DESC
        LIMIT 10
    ''')
    
    duplicates = cursor.fetchall()
    if duplicates:
        print("Top items with multiple entries:")
        for aircraft, item_num, count in duplicates:
            print(f"  {aircraft} - {item_num}: {count} entries")
    
    # Close database connection
    conn.close()
    
    print(f"\n💾 Enhanced database saved as: mmel_db.db")
    print(f"📊 This database preserves all entries including duplicates")
    print(f"🔍 Use sequence_number column to distinguish between duplicate item numbers")

if __name__ == "__main__":
    main()
