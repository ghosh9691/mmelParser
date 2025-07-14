import fitz

doc = fitz.open('A-320_Rev_31.pdf')

# Look at a specific page that should contain MMEL items
page = doc[30]  # Page 30 looks like it's in ATA 21 section
text = page.get_text('text')
lines = text.split('\n')

print("=== Full content of page 30 ===")
for i, line in enumerate(lines):
    print(f"{i:3d}: {line}")

print("\n=== Looking for MMEL patterns ===")
for i, line in enumerate(lines):
    if line.strip() and ('-' in line or 'ITEM' in line.upper()):
        print(f"Line {i}: {line}")
