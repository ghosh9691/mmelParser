import fitz
import re

def debug_actual_parser(pdf_path):
    doc = fitz.open(pdf_path)
    text = "\n".join(page.get_text("text") for page in doc)
    
    lines = text.splitlines()
    entries = []
    current_entry = None
    current_ata = ""
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line:
            i += 1
            continue

        # Detect ATA section
        ata_match = re.match(r"^(\d{2})\.\s+(.+)", line)
        if ata_match:
            current_ata = ata_match.group(1)
            i += 1
            continue

        # Match MMEL item number
        item_match = re.match(r"^(\d{2}-\d{2}-\d{2}(?:-\d{2})*)$", line)
        if item_match and current_ata:
            # Save previous entry if exists
            if current_entry:
                entries.append(current_entry)
            
            item_number = item_match.group(1)
            
            # Only process the first few items for debugging
            if len(entries) > 3:
                break
            
            print(f"\n=== Processing {item_number} ===")
            
            # Initialize variables
            title_parts = []
            deferral_category = ""
            qty_installed = 0
            qty_required = 0
            remarks = []
            
            j = i + 1
            state = "title"
            
            while j < len(lines):
                next_line = lines[j].strip()
                
                # Check if we've hit the next MMEL item
                if re.match(r"^(\d{2}-\d{2}-\d{2}(?:-\d{2})*)$", next_line):
                    break
                
                # Check if we've hit a new ATA section
                if re.match(r"^(\d{2})\.\s+(.+)", next_line):
                    break
                
                # Skip headers
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
                    if next_line in ["A", "B", "C", "D"]:
                        deferral_category = next_line
                        state = "qty_installed"
                        print(f"  Set category: {deferral_category}")
                    else:
                        title_parts.append(next_line)
                        print(f"  Added to title: {next_line}")
                elif state == "qty_installed":
                    if next_line.isdigit():
                        qty_installed = int(next_line)
                        state = "qty_required"
                        print(f"  Set qty_installed: {qty_installed}")
                    else:
                        if deferral_category:
                            remarks.append(next_line)
                            state = "remarks"
                            print(f"  Added to remarks: {next_line}")
                        else:
                            title_parts.append(next_line)
                            print(f"  Added to title: {next_line}")
                elif state == "qty_required":
                    qty_match = re.match(r"^(\d+)(?:\s+(.+))?", next_line)
                    if qty_match:
                        qty_required = int(qty_match.group(1))
                        if qty_match.group(2):
                            remarks.append(qty_match.group(2))
                        state = "remarks"
                        print(f"  Set qty_required: {qty_required}")
                    else:
                        remarks.append(next_line)
                        state = "remarks"
                        print(f"  Added to remarks: {next_line}")
                else:  # state == "remarks"
                    remarks.append(next_line)
                    print(f"  Added to remarks: {next_line}")
                
                j += 1
            
            # Create the entry
            current_entry = {
                "itemNumber": item_number,
                "title": " ".join(title_parts).strip(),
                "deferralCategory": deferral_category,
                "quantityInstalled": qty_installed,
                "quantityRequired": qty_required,
                "remarks": remarks
            }
            
            print(f"  Created entry: {current_entry}")
            
            # Move to the last processed line
            i = j - 1
        
        i += 1
    
    # Add the last entry
    if current_entry:
        entries.append(current_entry)
    
    return entries

# Test with the actual parser logic
entries = debug_actual_parser('A-320_Rev_31.pdf')
print(f"\nFinal entries: {len(entries)}")
for entry in entries:
    print(f"  {entry['itemNumber']}: {entry['quantityInstalled']}/{entry['quantityRequired']}")
