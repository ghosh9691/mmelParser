import fitz  # PyMuPDF
import re

def analyze_b747_8_mmel_pages():
    """Analyze B-747-8 MMEL pages for actual item format"""
    
    pdf_path = "B-747-8_Rev 7.pdf"
    
    try:
        doc = fitz.open(pdf_path)
        print(f"=== B747-8 MMEL PAGES ANALYSIS ===")
        
        # Based on TOC, ATA 21 should start around page 21-1
        # Let's check pages that likely contain MMEL items
        target_pages = [20, 25, 30, 35, 40, 45, 50, 55, 60]
        
        for page_num in target_pages:
            if page_num < len(doc):
                page = doc[page_num]
                text = page.get_text()
                
                print(f"\n=== PAGE {page_num + 1} ===")
                print(text[:1500])  # Show more content
                print("=" * 50)
                
                # Look for specific patterns in this page
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    line = line.strip()
                    if (re.search(r'\b\d{2}-\d{2}-\d{2}\b', line) or
                        re.search(r'\b-\d{2}-\d{2}\b', line) or
                        'may be inoperative' in line.lower()):
                        print(f"POTENTIAL ITEM LINE {i}: {line}")
                        # Show context
                        start = max(0, i-2)
                        end = min(len(lines), i+3)
                        print(f"CONTEXT: {lines[start:end]}")
                        print("-" * 30)
        
        doc.close()
        
    except Exception as e:
        print(f"Error analyzing B747-8: {e}")

if __name__ == "__main__":
    analyze_b747_8_mmel_pages()
