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
        
        # Find the item and show more context
        for i, line in enumerate(lines):
            if '21-21-01' in line:
                print(f"\nContext around 21-21-01:")
                for j in range(max(0, i-2), min(len(lines), i+15)):
                    line_stripped = lines[j].strip()
                    marker = ">>>" if j == i else "   "
                    print(f"{marker} {j:3d}: '{line_stripped}'")
                    
                    # Show what our parser logic would do
                    if j > i:
                        if line_stripped in ["A", "B", "C", "D"]:
                            print(f"       ^ CATEGORY: {line_stripped}")
                        elif line_stripped.isdigit():
                            print(f"       ^ NUMBER: {line_stripped}")
                        elif re.match(r"^(\d+)(?:\s+(.+))?", line_stripped):
                            match = re.match(r"^(\d+)(?:\s+(.+))?", line_stripped)
                            print(f"       ^ QTY_REQUIRED: {match.group(1)}, REMARKS: {match.group(2) if match.group(2) else 'None'}")
                break
        break
