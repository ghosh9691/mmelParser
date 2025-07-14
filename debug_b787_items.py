import fitz
import re

doc = fitz.open('B787_Rev_19_5_20_2025.pdf')

# Look for pages with actual MMEL items
for page_num in range(15, 50):
    page = doc[page_num]
    text = page.get_text('text')
    lines = text.split('\n')
    
    # Look for potential MMEL item patterns
    for i, line in enumerate(lines):
        # Boeing format might be different - look for patterns like "21-XX-XX"
        if re.match(r'^21-\d{2}-\d{2}', line.strip()):
            print(f"Found potential MMEL item on page {page_num}:")
            print(f"Line {i}: '{line.strip()}'")
            
            # Show context
            for j in range(max(0, i-2), min(len(lines), i+8)):
                marker = ">>>" if j == i else "   "
                print(f"{marker} {j:3d}: '{lines[j].strip()}'")
            print()
            break
    else:
        continue
    break  # Stop after finding first item
