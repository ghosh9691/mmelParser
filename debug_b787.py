import fitz

doc = fitz.open('B787_Rev_19_5_20_2025.pdf')
print(f'Total pages: {len(doc)}')

# Look at the first few pages to understand the structure
for page_num in range(min(10, len(doc))):
    page = doc[page_num]
    text = page.get_text('text')
    lines = text.split('\n')
    first_line = lines[0] if lines else ''
    print(f'Page {page_num}: {first_line[:80]}...')
    
    # Look for MMEL-like patterns
    for i, line in enumerate(lines[:20]):
        if '-' in line and any(c.isdigit() for c in line) and len(line.strip()) > 5:
            print(f'  Potential MMEL line: {line.strip()[:100]}')
            if i < 19:  # Show next line for context
                print(f'    Next line: {lines[i+1].strip()[:100]}')
        if 'ATA' in line.upper() or ('.' in line and any(c.isdigit() for c in line[:3])):
            print(f'  Potential ATA section: {line.strip()[:100]}')
