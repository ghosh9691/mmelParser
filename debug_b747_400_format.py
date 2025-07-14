import fitz  # PyMuPDF
import re

def analyze_b747_400_format():
    """Analyze B-747-400 format specifically"""
    
    pdf_path = "B-747-400_Rev_32.pdf"
    
    try:
        doc = fitz.open(pdf_path)
        print(f"=== B747-400 DETAILED ANALYSIS ===")
        
        # Look for actual MMEL content pages
        for page_num in range(20, min(50, len(doc))):
            page = doc[page_num]
            text = page.get_text()
            
            # Look for pages with MMEL items
            if "may be inoperative" in text.lower() and "21." in text:
                print(f"\n=== PAGE {page_num + 1} ===")
                print(text[:2000])
                break
        
        # Look for item patterns in the entire document
        print("\n=== SEARCHING FOR ITEM PATTERNS ===")
        all_patterns = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            lines = text.split('\n')
            
            for line in lines:
                line = line.strip()
                # Look for lines that start with numbers and dashes
                if re.match(r'^\d+\s*-\s*\d+\s*-\s*\d+', line):
                    all_patterns.append(f"Page {page_num + 1}: {line}")
                elif re.match(r'^\d+\s*-\s*\d+\s*[A-Z]?', line) and len(line) < 20:
                    all_patterns.append(f"Page {page_num + 1}: {line}")
        
        print("Found potential item patterns:")
        for pattern in all_patterns[:20]:  # Show first 20
            print(pattern)
            
        doc.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_b747_400_format()
