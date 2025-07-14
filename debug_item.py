import fitz

doc = fitz.open('A-320_Rev_31.pdf')

# Find the first real MMEL item (21-21-01)
for page_num in range(25, 35):
    page = doc[page_num]
    text = page.get_text('text')
    if '21-21-01' in text:
        print(f"Found 21-21-01 on page {page_num}")
        lines = text.split('\n')
        
        # Find the item and show context
        for i, line in enumerate(lines):
            if '21-21-01' in line:
                print(f"\nContext around 21-21-01:")
                for j in range(max(0, i-5), min(len(lines), i+10)):
                    marker = ">>>" if j == i else "   "
                    print(f"{marker} {j:3d}: '{lines[j]}'")
                break
        break
