import re
import json
import sys
from pathlib import Path
from typing import List, Dict
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF maintaining layout structure"""
    doc = fitz.open(pdf_path)
    text = "\n".join(page.get_text("text") for page in doc)
    return text

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
        # The format is: sequence_number item_description category qty_installed qty_required remarks
        # Examples: "03-04 BULK Cargo HEATER", "21-03 Forward Ventilation", "26-02 Avionics"
        
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

def main():
    if len(sys.argv) != 4:
        print("Usage: python mmel_parser.py <mmel_pdf_file> <output_json_file> <aircraft_type>")
        print("Example: python mmel_parser.py A-380.pdf a380_mmel.json A380")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    output_file = sys.argv[2]
    aircraft_type = sys.argv[3]
    
    if not Path(pdf_file).exists():
        print(f"Error: PDF file '{pdf_file}' not found.")
        sys.exit(1)
    
    print(f"Processing: {pdf_file}")
    
    # Extract text from PDF
    text = extract_text_from_pdf(pdf_file)
    
    # Parse MMEL entries based on aircraft type
    if aircraft_type.upper() == "A380":
        entries = parse_a380_mmel_entries(text, aircraft_type)
    else:
        print(f"Error: Aircraft type '{aircraft_type}' not supported by A-380 parser.")
        sys.exit(1)
    
    # Write to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
    
    print(f"Extracted {len(entries)} MMEL items to {output_file}")

if __name__ == "__main__":
    main()
