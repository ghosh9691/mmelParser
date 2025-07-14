import fitz
import re

doc = fitz.open('B787_Rev_19_5_20_2025.pdf')

# Look for pages with actual MMEL items more broadly
print("Searching for MMEL patterns in B787 file...")

for page_num in range(10, 60):
    page = doc[page_num]
    text = page.get_text('text')
    lines = text.split('\n')
    
    # Look for various patterns
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        
        # Look for item numbers in various formats
        if (re.match(r'^\d{2}-\d{2}-\d{2}', line_stripped) or
            re.match(r'^21-\d{2}-\d{2}', line_stripped) or
            re.match(r'^22-\d{2}-\d{2}', line_stripped) or
            re.match(r'^23-\d{2}-\d{2}', line_stripped)):
            print(f"Found item pattern on page {page_num}:")
            print(f"Line {i}: '{line_stripped}'")
            
            # Show context
            for j in range(max(0, i-2), min(len(lines), i+8)):
                marker = ">>>" if j == i else "   "
                print(f"{marker} {j:3d}: '{lines[j].strip()}'")
            print()
            
            # Only show first few matches
            if page_num > 15:
                break
    else:
        continue
    break  # Stop after finding first item
    
print("\nAlso looking for ATA section headers...")
for page_num in range(10, 30):
    page = doc[page_num]
    text = page.get_text('text')
    lines = text.split('\n')
    
    for line in lines:
        if re.match(r'^21\.\s', line.strip()) or re.match(r'^22\.\s', line.strip()):
            print(f"Page {page_num}: ATA section - '{line.strip()}'")
            break
