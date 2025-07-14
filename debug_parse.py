import fitz
import re

def debug_parse_item(text, item_num):
    lines = text.splitlines()
    
    for i, line in enumerate(lines):
        if item_num in line.strip():
            print(f"Found {item_num} at line {i}: '{line.strip()}'")
            
            # Simulate the parsing logic
            title_parts = []
            deferral_category = ""
            qty_installed = 0
            qty_required = 0
            remarks = []
            
            j = i + 1
            state = "title"
            
            print(f"\nParsing from line {j}:")
            
            while j < len(lines) and j < i + 10:  # Look at next 10 lines
                next_line = lines[j].strip()
                print(f"  Line {j}: '{next_line}' (state: {state})")
                
                if not next_line:
                    j += 1
                    continue
                
                # Check for next item
                if re.match(r"^(\d{2}-\d{2}-\d{2}(?:-\d{2})*)$", next_line):
                    print(f"    -> Hit next item, breaking")
                    break
                
                # Parse based on current state
                if state == "title":
                    if next_line in ["A", "B", "C", "D"]:
                        deferral_category = next_line
                        state = "qty_installed"
                        print(f"    -> Set category to '{next_line}', state -> qty_installed")
                    else:
                        title_parts.append(next_line)
                        print(f"    -> Added to title: '{next_line}'")
                elif state == "qty_installed":
                    if next_line.isdigit():
                        qty_installed = int(next_line)
                        state = "qty_required"
                        print(f"    -> Set qty_installed to {qty_installed}, state -> qty_required")
                    else:
                        if deferral_category:
                            remarks.append(next_line)
                            state = "remarks"
                            print(f"    -> Added to remarks: '{next_line}', state -> remarks")
                        else:
                            title_parts.append(next_line)
                            print(f"    -> Added to title: '{next_line}'")
                elif state == "qty_required":
                    qty_match = re.match(r"^(\d+)(?:\s+(.+))?", next_line)
                    if qty_match:
                        qty_required = int(qty_match.group(1))
                        if qty_match.group(2):
                            remarks.append(qty_match.group(2))
                        state = "remarks"
                        print(f"    -> Set qty_required to {qty_required}, remainder: '{qty_match.group(2) if qty_match.group(2) else 'None'}', state -> remarks")
                    else:
                        remarks.append(next_line)
                        state = "remarks"
                        print(f"    -> Added to remarks: '{next_line}', state -> remarks")
                else:  # state == "remarks"
                    remarks.append(next_line)
                    print(f"    -> Added to remarks: '{next_line}'")
                
                j += 1
            
            print(f"\nFinal results:")
            print(f"  Title: '{' '.join(title_parts)}'")
            print(f"  Category: '{deferral_category}'")
            print(f"  Qty Installed: {qty_installed}")
            print(f"  Qty Required: {qty_required}")
            print(f"  Remarks: {remarks}")
            
            return

doc = fitz.open('A-320_Rev_31.pdf')

# Find the page with 21-21-01
for page_num in range(25, 35):
    page = doc[page_num]
    text = page.get_text('text')
    if '21-21-01' in text:
        debug_parse_item(text, '21-21-01')
        break
