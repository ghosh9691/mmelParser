import fitz
import re

doc = fitz.open('A-320_Rev_31.pdf')

# Find the page with 21-21-01
for page_num in range(25, 35):
    page = doc[page_num]
    text = page.get_text('text')
    if '21-21-01' in text:
        print(f"Found 21-21-01 on page {page_num}")
        lines = text.split('\n')
        
        # Find the item and show context
        for i, line in enumerate(lines):
            if '21-21-01' in line:
                print(f"\nAll lines from {i} to {i+10}:")
                for j in range(i, min(len(lines), i+10)):
                    line_stripped = lines[j].strip()
                    print(f"  {j:3d}: '{line_stripped}'")
                
                # Now simulate exactly what the debug script does
                print(f"\nSimulating debug script logic:")
                j = i + 1
                while j < len(lines) and j < i + 10:
                    next_line = lines[j].strip()
                    print(f"  Processing line {j}: '{next_line}'")
                    
                    # Check skip conditions
                    if (not next_line or 
                        next_line in ["Item", "Change", "Bar", "Sequence No."] or
                        next_line.startswith("U.S. DEPARTMENT OF TRANSPORTATION") or
                        next_line.startswith("FEDERAL AVIATION ADMINISTRATION")):
                        print(f"    -> SKIPPED (header filter)")
                        j += 1
                        continue
                    
                    print(f"    -> PROCESSED")
                    j += 1
                    
                    if j > i + 6:  # Stop after a few lines
                        break
                break
        break
