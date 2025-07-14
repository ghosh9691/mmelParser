import fitz  # PyMuPDF
import re

def analyze_a380_mmel_pages():
    """Analyze A380 MMEL pages for actual item format"""
    
    pdf_path = "A-380 R0.pdf"
    
    try:
        doc = fitz.open(pdf_path)
        print(f"=== A380 MMEL PAGES ANALYSIS ===")
        
        # Look for pages that contain actual MMEL items
        # Based on TOC, ATA 21 starts around page 21-1
        
        # Check pages that likely contain MMEL items
        target_pages = [15, 16, 17, 18, 19, 20, 25, 30, 35, 40]
        
        for page_num in target_pages:
            if page_num < len(doc):
                page = doc[page_num]
                text = page.get_text()
                
                print(f"\n=== PAGE {page_num + 1} ===")
                print(text[:1000])
                print("=" * 50)
                
                # Look for any number patterns
                patterns = [
                    r'\b\d{2}-\d{2}-\d{2}[A-Z]?\b',  # Standard with optional letter
                    r'\b\d{2}-\d{2}-\d{2}-\d{2}[A-Z]?\b',  # Extended format
                    r'\b\d{2}\.\d{2}\.\d{2}[A-Z]?\b',  # Dot format
                    r'\b\d+[A-Z]?\s*-\s*\d+[A-Z]?\s*-\s*\d+[A-Z]?\b',  # Spaced format
                    r'\([A-Z]\)\s*\d+\s*-\s*\d+\s*-\s*\d+',  # With category prefix
                    r'\d+\s*-\s*\d+\s*-\s*\d+\s*[A-Z]',  # With category suffix
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, text)
                    if matches:
                        print(f"Found pattern {pattern}: {matches[:5]}")
        
        # Look specifically for lines that might contain item numbers
        print("\n=== SEARCHING FOR ITEM-LIKE LINES ===")
        
        for page_num in range(15, min(50, len(doc))):
            page = doc[page_num]
            text = page.get_text()
            lines = text.split('\n')
            
            for line in lines:
                line = line.strip()
                # Look for lines that might be MMEL items
                if (len(line) > 10 and 
                    ('may be inoperative' in line.lower() or 
                     'inoperative provided' in line.lower() or
                     line.startswith('(') or
                     any(cat in line for cat in ['Category A', 'Category B', 'Category C', 'Category D']) or
                     re.search(r'\b[A-D]\b.*\d+.*\d+', line))):
                    print(f"Page {page_num + 1}: {line[:100]}...")
                    if page_num > 25:  # Don't show too many
                        break
            
            if page_num > 25:
                break
        
        doc.close()
        
    except Exception as e:
        print(f"Error analyzing A380 MMEL pages: {e}")
        return False
    
    return True

if __name__ == "__main__":
    analyze_a380_mmel_pages()
