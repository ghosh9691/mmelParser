import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path

def create_mmel_database():
    """Create SQLite database and tables for MMEL data"""
    
    # Create database connection
    conn = sqlite3.connect('mmel_database.db')
    cursor = conn.cursor()
    
    # Create main MMEL items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mmel_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aircraft_type TEXT NOT NULL,
            ata_chapter TEXT NOT NULL,
            item_number TEXT NOT NULL,
            title TEXT NOT NULL,
            deferral_category TEXT,
            quantity_installed INTEGER DEFAULT 0,
            quantity_required INTEGER DEFAULT 0,
            remarks_summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(aircraft_type, item_number)
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
    
    # Create aircraft summary table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aircraft_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aircraft_type TEXT UNIQUE NOT NULL,
            total_items INTEGER,
            total_category_a INTEGER DEFAULT 0,
            total_category_b INTEGER DEFAULT 0,
            total_category_c INTEGER DEFAULT 0,
            total_category_d INTEGER DEFAULT 0,
            total_empty_category INTEGER DEFAULT 0,
            items_with_maintenance_procedures INTEGER DEFAULT 0,
            items_with_operational_procedures INTEGER DEFAULT 0,
            items_with_remarks INTEGER DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_aircraft_type ON mmel_items (aircraft_type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_ata_chapter ON mmel_items (ata_chapter)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_item_number ON mmel_items (item_number)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_deferral_category ON mmel_items (deferral_category)')
    
    conn.commit()
    return conn

def insert_mmel_data(conn, json_file_path):
    """Insert MMEL data from JSON file into database"""
    
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
                # Insert main MMEL item
                cursor.execute('''
                    INSERT OR REPLACE INTO mmel_items (
                        aircraft_type, ata_chapter, item_number, title, 
                        deferral_category, quantity_installed, quantity_required, 
                        remarks_summary
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item.get('aircraftType', ''),
                    item.get('ataChapter', ''),
                    item.get('itemNumber', ''),
                    item.get('title', ''),
                    item.get('deferralCategory', ''),
                    item.get('quantityInstalled', 0),
                    item.get('quantityRequired', 0),
                    item.get('remarks', {}).get('summary', '')
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

def update_aircraft_summary(conn):
    """Update aircraft summary statistics"""
    
    cursor = conn.cursor()
    
    # Get all aircraft types
    cursor.execute('SELECT DISTINCT aircraft_type FROM mmel_items')
    aircraft_types = [row[0] for row in cursor.fetchall()]
    
    for aircraft_type in aircraft_types:
        # Count total items
        cursor.execute('SELECT COUNT(*) FROM mmel_items WHERE aircraft_type = ?', (aircraft_type,))
        total_items = cursor.fetchone()[0]
        
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
        
        # Insert or update summary
        cursor.execute('''
            INSERT OR REPLACE INTO aircraft_summary (
                aircraft_type, total_items, total_category_a, total_category_b, 
                total_category_c, total_category_d, total_empty_category,
                items_with_maintenance_procedures, items_with_operational_procedures,
                items_with_remarks, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            aircraft_type, total_items, category_a, category_b, category_c, category_d,
            empty_category, items_with_maintenance, items_with_operational, items_with_remarks
        ))
    
    conn.commit()

def main():
    """Main function to process all MMEL JSON files"""
    
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
    
    # Create database
    print("Creating MMEL database...")
    conn = create_mmel_database()
    
    total_items = 0
    processed_files = 0
    
    # Process each JSON file
    for json_file in json_files:
        if os.path.exists(json_file):
            items_count = insert_mmel_data(conn, json_file)
            total_items += items_count
            processed_files += 1
            print(f"✅ {json_file}: {items_count} items inserted")
        else:
            print(f"❌ {json_file}: File not found")
    
    # Update aircraft summary statistics
    print("\nUpdating aircraft summary statistics...")
    update_aircraft_summary(conn)
    
    # Display summary
    print(f"\n🎯 DATABASE CREATION COMPLETE!")
    print(f"📁 Processed files: {processed_files}")
    print(f"📊 Total MMEL items inserted: {total_items:,}")
    
    # Show aircraft summary
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM aircraft_summary ORDER BY aircraft_type')
    summaries = cursor.fetchall()
    
    print(f"\n📋 AIRCRAFT SUMMARY:")
    print("Aircraft Type | Total Items | Cat A | Cat B | Cat C | Cat D | Empty | Maint | Ops | Remarks")
    print("-" * 90)
    
    for summary in summaries:
        aircraft_type = summary[1]
        total = summary[2]
        cat_a = summary[3]
        cat_b = summary[4]
        cat_c = summary[5]
        cat_d = summary[6]
        empty = summary[7]
        maint = summary[8]
        ops = summary[9]
        remarks = summary[10]
        
        print(f"{aircraft_type:>12} | {total:>10} | {cat_a:>5} | {cat_b:>5} | {cat_c:>5} | {cat_d:>5} | {empty:>5} | {maint:>5} | {ops:>3} | {remarks:>7}")
    
    # Close database connection
    conn.close()
    
    print(f"\n💾 Database saved as: mmel_database.db")
    print(f"📊 Use SQLite browser or SQL queries to explore the data")

if __name__ == "__main__":
    main()
