import fitz
import re

doc = fitz.open('B787_Rev_19_5_20_2025.pdf')

# Look at page 11 which has ATA 21 content
page = doc[11]
text = page.get_text('text')
lines = text.split('\n')

print("=== Full content of page 11 ===")
for i, line in enumerate(lines):
    print(f"{i:3d}: '{line.strip()}'")

print("\n=== Looking for patterns that might be MMEL items ===")
for i, line in enumerate(lines):
    line_stripped = line.strip()
    # Look for any line that might contain item numbers
    if (re.search(r'\d{2}-\d{2}-\d{2}', line_stripped) or
        (len(line_stripped) > 3 and '-' in line_stripped and any(c.isdigit() for c in line_stripped))):
        print(f"Line {i}: '{line_stripped}'")
        # Show context
        for j in range(max(0, i-1), min(len(lines), i+3)):
            marker = ">>>" if j == i else "   "
            print(f"{marker} {j:3d}: '{lines[j].strip()}'")
        print()
