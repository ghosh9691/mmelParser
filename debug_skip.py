import fitz

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
                print(f"\nLines around 21-21-01:")
                for j in range(max(0, i), min(len(lines), i+10)):
                    line_stripped = lines[j].strip()
                    print(f"  {j:3d}: '{line_stripped}'")
                    
                    # Check if this line would be skipped by our header filter
                    if (not line_stripped or 
                        line_stripped in ["Item", "1", "2", "3", "4", "Change", "Bar", "Sequence No."] or
                        line_stripped.startswith("U.S. DEPARTMENT OF TRANSPORTATION")):
                        print(f"       ^ WOULD BE SKIPPED BY HEADER FILTER")
                break
        break
