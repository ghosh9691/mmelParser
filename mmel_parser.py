import re
import json
import sys
from pathlib import Path
from typing import List, Dict
import fitz  # PyMuPDF

# Step 1: Extract layout-preserved text from PDF
def extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    text = "\n".join(page.get_text("text") for page in doc)
    return text

# Step 2: Identify MMEL item lines and parse them into structured objects
def parse_mmel_entries(text: str, aircraft_type: str) -> List[Dict]:
    entries = []
    current_entry = None
    current_ata = ""
    lines = text.splitlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line:
            i += 1
            continue

        # Detect ATA section (e.g., "21. Air Conditioning")
        ata_match = re.match(r"^(\d{2})\.\s+(.+)", line)
        if ata_match:
            current_ata = ata_match.group(1)
            i += 1
            continue

        # Match a new MMEL item number 
        # Airbus format: "21-21-01" or Boeing format: "-21-01"
        item_match = re.match(r"^(\d{2}-\d{2}-\d{2}(?:-\d{2})*)$", line)  # Airbus format
        boeing_match = re.match(r"^(-\d{2}-\d{2}(?:-\d{2})*)$", line)      # Boeing format
        
        if (item_match or boeing_match) and current_ata:
            # Save previous entry if exists
            if current_entry:
                entries.append(current_entry)
            
            if item_match:
                item_number = item_match.group(1)
            else:
                # Boeing format: add current ATA prefix to the item number
                boeing_item = boeing_match.group(1)
                item_number = current_ata + boeing_item  # e.g., "21" + "-21-01" = "21-21-01"
            
            # Parse the entry structure
            title_parts = []
            deferral_category = ""
            qty_installed = 0
            qty_required = 0
            remarks = []
            
            # Look ahead to gather title, category, quantities, and remarks
            j = i + 1
            state = "title"  # title -> category -> qty_installed -> qty_required -> remarks
            
            while j < len(lines):
                next_line = lines[j].strip()
                
                # Check if we've hit the next MMEL item
                if (re.match(r"^(\d{2}-\d{2}-\d{2}(?:-\d{2})*)$", next_line) or
                    re.match(r"^(-\d{2}-\d{2}(?:-\d{2})*)$", next_line)):
                    break
                
                # Check if we've hit a new ATA section
                if re.match(r"^(\d{2})\.\s+(.+)", next_line):
                    break
                
                # Skip empty lines, table headers, and page headers
                if (not next_line or 
                    next_line in ["Item", "Change", "Bar", "Sequence No."] or
                    next_line.startswith("U.S. DEPARTMENT OF TRANSPORTATION") or
                    next_line.startswith("FEDERAL AVIATION ADMINISTRATION") or
                    next_line.startswith("MASTER MINIMUM EQUIPMENT LIST") or
                    next_line.startswith("REVISION NO.") or
                    next_line.startswith("DATE:") or
                    next_line.startswith("PAGE NO.") or
                    next_line.startswith("AIRCRAFT:") or
                    next_line.startswith("Airbus") or
                    next_line.startswith("TABLE KEY") or
                    next_line.startswith("1. REPAIR CATEGORY") or
                    next_line.startswith("2. NO. INSTALLED") or
                    next_line.startswith("3. NO. REQUIRED") or
                    next_line.startswith("4. REMARKS OR EXCEPTIONS")):
                    j += 1
                    continue
                
                # Parse based on current state
                if state == "title":
                    # Category letters are single characters A, B, C, or D on their own line
                    if next_line in ["A", "B", "C", "D"]:
                        deferral_category = next_line
                        state = "qty_installed"
                    else:
                        # Still part of title
                        title_parts.append(next_line)
                elif state == "qty_installed":
                    # Should be a number
                    if next_line.isdigit():
                        qty_installed = int(next_line)
                        state = "qty_required"
                    else:
                        # If not a digit, assume it's still part of title or remarks
                        if deferral_category:  # We already have category, this must be remarks
                            remarks.append(next_line)
                            state = "remarks"
                        else:
                            title_parts.append(next_line)
                elif state == "qty_required":
                    # Look for pattern like "0 (M)(O) May be inoperative..." or just "0"
                    qty_match = re.match(r"^(\d+)(?:\s+(.+))?", next_line)
                    if qty_match:
                        qty_required = int(qty_match.group(1))
                        if qty_match.group(2):
                            remarks.append(qty_match.group(2))
                        state = "remarks"
                    else:
                        # Not a quantity pattern, treat as remark
                        remarks.append(next_line)
                        state = "remarks"
                else:  # state == "remarks"
                    # Everything else is remarks
                    remarks.append(next_line)
                
                j += 1
            
            # Create the entry
            current_entry = {
                "aircraftType": aircraft_type,
                "ataChapter": current_ata,
                "itemNumber": item_number,
                "title": " ".join(title_parts).strip(),
                "deferralCategory": deferral_category,
                "quantityInstalled": qty_installed,
                "quantityRequired": qty_required,
                "remarks": {
                    "summary": "",
                    "steps": []
                },
                "maintenanceProcedures": [],
                "operationalProcedures": [],
            }
            
            # Process remarks to categorize them
            full_remarks = " ".join(remarks).strip()
            current_entry["remarks"]["summary"] = full_remarks
            
            # Extract maintenance and operational procedures
            for remark in remarks:
                if "(M)" in remark:
                    current_entry["maintenanceProcedures"].append(remark.strip())
                if "(O)" in remark:
                    current_entry["operationalProcedures"].append(remark.strip())
                
                # Extract bullet points
                bullet_match = re.match(r"^\(?[a-zA-Z]\)?[\.\)]\s*(.+)", remark)
                if bullet_match:
                    current_entry["remarks"]["steps"].append(bullet_match.group(1).strip())
            
            # Move to the last processed line
            i = j - 1
        
        i += 1
    
    # Add the last entry
    if current_entry:
        entries.append(current_entry)

    return entries


def parse_a380_mmel_entries(text: str, aircraft_type: str) -> List[Dict]:
    """Parse A-380 MMEL entries with tabular format"""
    entries = []
    lines = text.splitlines()
    current_ata = ""
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line:
            i += 1
            continue
        
        # Detect ATA section header (e.g., "21  AIR CONDITIONING")
        ata_match = re.match(r"^(\d{2})\s+(.+)", line)
        if ata_match and len(ata_match.group(2)) > 3:  # Ensure it's a section header
            current_ata = ata_match.group(1)
            i += 1
            continue
        
        # Skip table headers and page headers
        if (line.startswith("U.S. DEPARTMENT OF TRANSPORTATION") or
            line.startswith("FEDERAL AVIATION ADMINISTRATION") or
            line.startswith("MASTER MINIMUM EQUIPMENT LIST") or
            line.startswith("AIRCRAFT:") or
            line.startswith("REVISION NO") or
            line.startswith("DATE:") or
            line.startswith("PAGE:") or
            line.startswith("SYSTEM &") or
            line.startswith("SEQUENCE") or
            line.startswith("ITEM") or
            line.startswith("NUMBER") or
            line.startswith("REQUIRED FOR DISPATCH") or
            line.startswith("REMARKS OR EXCEPTIONS") or
            line.startswith("1.") or
            line.startswith("2.") or
            line.startswith("3.") or
            line.startswith("4.") or
            line == "A-380"):
            i += 1
            continue
        
        # Look for MMEL item patterns in A-380 format
        # Pattern 1: Two-digit sequence (like "03-04")
        seq_match = re.match(r"^(\d{2}-\d{2})\s+(.+)", line)
        # Pattern 2: Three-digit sequence (like "21-03")  
        full_match = re.match(r"^(\d{2}-\d{2}-\d{2})\s+(.+)", line)
        
        if seq_match or full_match:
            if full_match:
                item_number = full_match.group(1)
                remaining_text = full_match.group(2)
            else:
                # For sequences like "03-04", prepend current ATA chapter
                seq_number = seq_match.group(1)
                item_number = f"{current_ata}-{seq_number}"
                remaining_text = seq_match.group(2)
            
            # Parse the remaining text to extract title, category, quantities, and remarks
            title_parts = []
            deferral_category = ""
            qty_installed = 0
            qty_required = 0
            remarks_parts = []
            
            # Look for category and quantities in the remaining text and subsequent lines
            title_line = remaining_text
            
            # Look ahead to collect full entry information
            j = i + 1
            entry_lines = [title_line]
            
            while j < len(lines):
                next_line = lines[j].strip()
                
                # Stop if we hit another MMEL item
                if (re.match(r"^(\d{2}-\d{2})\s+(.+)", next_line) or
                    re.match(r"^(\d{2}-\d{2}-\d{2})\s+(.+)", next_line)):
                    break
                
                # Stop if we hit a new ATA section
                if re.match(r"^(\d{2})\s+(.+)", next_line) and len(next_line.split()) > 1:
                    break
                
                # Skip headers and empty lines
                if (not next_line or
                    next_line.startswith("U.S. DEPARTMENT OF TRANSPORTATION") or
                    next_line.startswith("FEDERAL AVIATION ADMINISTRATION") or
                    next_line.startswith("MASTER MINIMUM EQUIPMENT LIST") or
                    next_line.startswith("AIRCRAFT:") or
                    next_line.startswith("REVISION NO") or
                    next_line.startswith("DATE:") or
                    next_line.startswith("PAGE:") or
                    next_line.startswith("SYSTEM &") or
                    next_line.startswith("SEQUENCE") or
                    next_line.startswith("ITEM") or
                    next_line.startswith("NUMBER") or
                    next_line.startswith("REQUIRED FOR DISPATCH") or
                    next_line.startswith("REMARKS OR EXCEPTIONS") or
                    next_line.startswith("1.") or
                    next_line.startswith("2.") or
                    next_line.startswith("3.") or
                    next_line.startswith("4.") or
                    next_line == "A-380"):
                    j += 1
                    continue
                
                entry_lines.append(next_line)
                j += 1
            
            # Parse the collected entry lines
            all_text = " ".join(entry_lines)
            
            # Extract title (everything before category)
            title_match = re.match(r"^(.+?)\s+([A-D])\s+(\d+)\s+(\d+)\s*(.*)$", all_text)
            if title_match:
                title = title_match.group(1).strip()
                deferral_category = title_match.group(2)
                qty_installed = int(title_match.group(3))
                qty_required = int(title_match.group(4))
                remarks_text = title_match.group(5).strip()
            else:
                # Try alternative pattern where category might be on separate line
                title_parts = []
                category_found = False
                
                for entry_line in entry_lines:
                    # Check if this line contains a single category letter
                    if not category_found and entry_line in ["A", "B", "C", "D"]:
                        deferral_category = entry_line
                        category_found = True
                        continue
                    
                    # Check if this line contains quantities
                    qty_match = re.match(r"^([A-D])\s+(\d+)\s+(\d+)", entry_line)
                    if qty_match:
                        deferral_category = qty_match.group(1)
                        qty_installed = int(qty_match.group(2))
                        qty_required = int(qty_match.group(3))
                        # Rest of the line is remarks
                        remarks_text = entry_line[len(qty_match.group(0)):].strip()
                        break
                    
                    # Check for quantity patterns without category
                    qty_only_match = re.match(r"^(\d+)\s+(\d+)", entry_line)
                    if qty_only_match and not category_found:
                        qty_installed = int(qty_only_match.group(1))
                        qty_required = int(qty_only_match.group(2))
                        remarks_text = entry_line[len(qty_only_match.group(0)):].strip()
                        break
                    
                    # Otherwise, add to title
                    if not category_found:
                        title_parts.append(entry_line)
                    else:
                        # Add to remarks
                        remarks_parts.append(entry_line)
                
                title = " ".join(title_parts).strip()
                if not title and entry_lines:
                    title = entry_lines[0].strip()
                
                if remarks_parts:
                    remarks_text = " ".join(remarks_parts).strip()
            
            # Clean up title - remove "***" markers
            title = re.sub(r'\*\*\*', '', title).strip()
            
            # Parse remarks to extract maintenance and operational procedures
            maintenance_procedures = []
            operational_procedures = []
            remarks_summary = remarks_text
            
            # Look for (M) and (O) patterns in remarks
            if remarks_text:
                # Split by (M) and (O) patterns
                parts = re.split(r'\(([MO])\)', remarks_text)
                current_type = None
                
                for part in parts:
                    part = part.strip()
                    if part in ['M', 'O']:
                        current_type = part
                    elif part and current_type:
                        if current_type == 'M':
                            maintenance_procedures.append(f"({current_type}){part}")
                        else:
                            operational_procedures.append(f"({current_type}){part}")
                
                # If no specific procedures found, treat as general remark
                if not maintenance_procedures and not operational_procedures and remarks_text:
                    if '(M)' in remarks_text:
                        maintenance_procedures.append(remarks_text)
                    elif '(O)' in remarks_text:
                        operational_procedures.append(remarks_text)
            
            # Create MMEL entry
            entry = {
                "aircraftType": aircraft_type,
                "ataChapter": current_ata,
                "itemNumber": item_number,
                "title": title,
                "deferralCategory": deferral_category,
                "quantityInstalled": qty_installed,
                "quantityRequired": qty_required,
                "remarks": {
                    "summary": remarks_summary,
                    "steps": []
                },
                "maintenanceProcedures": maintenance_procedures,
                "operationalProcedures": operational_procedures
            }
            
            entries.append(entry)
            i = j - 1  # Continue from where we left off
        
        i += 1
    
    return entries


def parse_b747_400_mmel_entries(text: str, aircraft_type: str) -> List[Dict]:
    """Parse B-747-400 MMEL entries with Boeing tabular format"""
    entries = []
    lines = text.splitlines()
    current_ata = ""
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line:
            i += 1
            continue
        
        # Detect ATA section header (e.g., "21. Air Conditioning")
        ata_match = re.match(r"^(\d{2})\.\s+(.+)", line)
        if ata_match:
            current_ata = ata_match.group(1)
            i += 1
            continue
        
        # Skip table headers and page headers
        if (line.startswith("U.S. DEPARTMENT OF TRANSPORTATION") or
            line.startswith("FEDERAL AVIATION ADMINISTRATION") or
            line.startswith("MASTER MINIMUM EQUIPMENT LIST") or
            line.startswith("AIRCRAFT:") or
            line.startswith("REVISION NO") or
            line.startswith("DATE:") or
            line.startswith("PAGE NO") or
            line.startswith("TABLE KEY") or
            line.startswith("1. REPAIR CATEGORY") or
            line.startswith("2. NO. INSTALLED") or
            line.startswith("3. NO. REQUIRED") or
            line.startswith("4. REMARKS OR EXCEPTIONS") or
            line.startswith("Sequence No.") or
            line.startswith("Item") or
            line.startswith("Change") or
            line.startswith("Bar") or
            line in ["1", "2", "3", "4"] or
            line.startswith("B-747-400") or
            line.startswith("TABLE OF CONTENTS") or
            line.startswith("SYSTEM NO.") or
            line.startswith("SYSTEM") or
            line.startswith("PAGE NO.") or
            line.startswith("REV NO.") or
            line.startswith("HIGHLIGHTS OF CHANGE") or
            "thru" in line):  # Skip table of contents entries
            i += 1
            continue
        
        # Look for MMEL item patterns in B747-400 format
        # Pattern: sequence like "31-1", "32-2", etc.
        seq_match = re.match(r"^(\d{2}-\d{1,2})\s+(.+)", line)
        # Also check for patterns like "31-1A" or "31-1B"
        seq_alpha_match = re.match(r"^(\d{2}-\d{1,2}[A-Z])\s+(.+)", line)
        
        if seq_match or seq_alpha_match:
            if seq_alpha_match:
                seq_number = seq_alpha_match.group(1)
                remaining_text = seq_alpha_match.group(2)
            else:
                seq_number = seq_match.group(1)
                remaining_text = seq_match.group(2)
            
            # Create full item number with ATA chapter
            item_number = f"{current_ata}-{seq_number}"
            
            # Parse the remaining text to extract title, category, quantities, and remarks
            title_parts = []
            deferral_category = ""
            qty_installed = 0
            qty_required = 0
            remarks_parts = []
            
            # Look ahead to collect full entry information
            j = i + 1
            entry_lines = [remaining_text]
            
            while j < len(lines):
                next_line = lines[j].strip()
                
                # Stop if we hit another MMEL item
                if (re.match(r"^(\d{2}-\d{1,2})\s+(.+)", next_line) or
                    re.match(r"^(\d{2}-\d{1,2}[A-Z])\s+(.+)", next_line)):
                    break
                
                # Stop if we hit a new ATA section
                if re.match(r"^(\d{2})\.\s+(.+)", next_line):
                    break
                
                # Skip headers and empty lines
                if (not next_line or
                    next_line.startswith("U.S. DEPARTMENT OF TRANSPORTATION") or
                    next_line.startswith("FEDERAL AVIATION ADMINISTRATION") or
                    next_line.startswith("MASTER MINIMUM EQUIPMENT LIST") or
                    next_line.startswith("AIRCRAFT:") or
                    next_line.startswith("REVISION NO") or
                    next_line.startswith("DATE:") or
                    next_line.startswith("PAGE NO") or
                    next_line.startswith("TABLE KEY") or
                    next_line.startswith("1. REPAIR CATEGORY") or
                    next_line.startswith("2. NO. INSTALLED") or
                    next_line.startswith("3. NO. REQUIRED") or
                    next_line.startswith("4. REMARKS OR EXCEPTIONS") or
                    next_line.startswith("Sequence No.") or
                    next_line.startswith("Item") or
                    next_line.startswith("Change") or
                    next_line.startswith("Bar") or
                    next_line in ["1", "2", "3", "4"] or
                    next_line.startswith("B-747-400") or
                    next_line.startswith("|")):  # Skip continuation bars
                    j += 1
                    continue
                
                entry_lines.append(next_line)
                j += 1
            
            # Parse the collected entry lines
            all_text = " ".join(entry_lines)
            
            # Try to parse category, quantities, and remarks
            # Look for pattern: title [category] [qty1] [qty2] remarks
            # B747-400 format: "item_desc C 2 0 (M)(O) May be inoperative..."
            
            # First try to find category and quantities in the text
            category_qty_match = re.search(r'\b([A-D])\s+(\d+)\s+(\d+)\s+(.+)', all_text)
            if category_qty_match:
                # Extract title (everything before the category)
                title_end = all_text.find(category_qty_match.group(0))
                title = all_text[:title_end].strip()
                
                deferral_category = category_qty_match.group(1)
                qty_installed = int(category_qty_match.group(2))
                qty_required = int(category_qty_match.group(3))
                remarks_text = category_qty_match.group(4).strip()
            else:
                # Try alternative parsing
                title_parts = []
                category_found = False
                
                for entry_line in entry_lines:
                    # Check if this line contains category and quantities
                    cat_qty_match = re.match(r'^([A-D])\s+(\d+)\s+(\d+)\s*(.*)$', entry_line)
                    if cat_qty_match:
                        deferral_category = cat_qty_match.group(1)
                        qty_installed = int(cat_qty_match.group(2))
                        qty_required = int(cat_qty_match.group(3))
                        remarks_text = cat_qty_match.group(4).strip()
                        category_found = True
                        break
                    
                    # Check for standalone category
                    if not category_found and entry_line in ["A", "B", "C", "D"]:
                        deferral_category = entry_line
                        category_found = True
                        continue
                    
                    # Otherwise, add to title or remarks
                    if not category_found:
                        title_parts.append(entry_line)
                    else:
                        remarks_parts.append(entry_line)
                
                title = " ".join(title_parts).strip()
                if not title and entry_lines:
                    title = entry_lines[0].strip()
                
                if remarks_parts:
                    remarks_text = " ".join(remarks_parts).strip()
                else:
                    remarks_text = ""
            
            # Clean up title
            title = re.sub(r'\s+', ' ', title).strip()
            
            # Parse remarks to extract maintenance and operational procedures
            maintenance_procedures = []
            operational_procedures = []
            remarks_summary = remarks_text
            
            # Look for (M) and (O) patterns in remarks
            if remarks_text:
                # Split by (M) and (O) patterns
                parts = re.split(r'\(([MO])\)', remarks_text)
                current_type = None
                
                for part in parts:
                    part = part.strip()
                    if part in ['M', 'O']:
                        current_type = part
                    elif part and current_type:
                        if current_type == 'M':
                            maintenance_procedures.append(f"({current_type}){part}")
                        else:
                            operational_procedures.append(f"({current_type}){part}")
                
                # If no specific procedures found, treat as general remark
                if not maintenance_procedures and not operational_procedures and remarks_text:
                    if '(M)' in remarks_text:
                        maintenance_procedures.append(remarks_text)
                    elif '(O)' in remarks_text:
                        operational_procedures.append(remarks_text)
            
            # Create MMEL entry
            entry = {
                "aircraftType": aircraft_type,
                "ataChapter": current_ata,
                "itemNumber": item_number,
                "title": title,
                "deferralCategory": deferral_category,
                "quantityInstalled": qty_installed,
                "quantityRequired": qty_required,
                "remarks": {
                    "summary": remarks_summary,
                    "steps": []
                },
                "maintenanceProcedures": maintenance_procedures,
                "operationalProcedures": operational_procedures
            }
            
            entries.append(entry)
            i = j - 1  # Continue from where we left off
        
        i += 1
    
    return entries


# Step 3: Main function
def main(pdf_path: str, output_path: str, aircraft_type: str):
    print(f"Processing: {pdf_path}")
    text = extract_text_from_pdf(pdf_path)
    
    # Select parser based on aircraft type
    if aircraft_type == "A380":
        entries = parse_a380_mmel_entries(text, aircraft_type)
    elif aircraft_type == "B747-400":
        entries = parse_b747_400_mmel_entries(text, aircraft_type)
    else:
        entries = parse_mmel_entries(text, aircraft_type)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

    print(f"Extracted {len(entries)} MMEL items to {output_path}")

# CLI usage
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python mmel_parser.py <mmel_pdf_file> <output_json_file> <aircraft_type>")
        print("Example: python mmel_parser.py A-320_Rev_31.pdf a320_mmel.json A320")
        sys.exit(1)

    pdf_file = sys.argv[1]
    json_output = sys.argv[2]
    aircraft = sys.argv[3]

    main(pdf_file, json_output, aircraft)
