import fitz

doc = fitz.open('A-320_Rev_31.pdf')
print(f'Total pages: {len(doc)}')

# Look for pages with MMEL items
for i in range(20, 50):
    text = doc[i].get_text('text')
    lines = text.split('\n')
    first_line = lines[0] if lines else ''
    print(f'Page {i}: {first_line[:80]}...')
    
    # Look for patterns that might indicate MMEL items
    for line in lines[:10]:
        if '-' in line and any(c.isdigit() for c in line):
            print(f'  Potential MMEL line: {line[:100]}')
