import fitz

doc = fitz.open('A-320_Rev_31.pdf')

# Look at a few more pages to understand the pattern
for page_num in [35, 40, 45]:
    page = doc[page_num]
    text = page.get_text('text')
    lines = text.split('\n')
    
    print(f"\n=== Page {page_num} ===")
    for i, line in enumerate(lines):
        if line.strip() and (line.strip().startswith('2') or '-' in line):
            print(f"Line {i}: '{line.strip()}'")
            # Show next few lines for context
            for j in range(1, 5):
                if i + j < len(lines):
                    print(f"  +{j}: '{lines[i + j].strip()}'")
            print()
