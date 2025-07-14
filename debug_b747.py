import fitz  # PyMuPDF
import re
import os

def debug_b747_pdfs():
    """Debug Boeing 747 PDF files to understand their format"""
    
    b747_files = [
        "B-747-400LCF_Rev 3.pdf",
        "B-747-400_Rev_32.pdf", 
        "B-747-8_Rev 7.pdf"
    ]
    
    for pdf_file in b747_files:
        if not os.path.exists(pdf_file):
            print(f"File not found: {pdf_file}")
            continue
            
        print(f"\n=== ANALYZING {pdf_file} ===")
        
        try:
            doc = fitz.open(pdf_file)
            print(f"Total pages: {len(doc)}")
            
            # Check first few pages for structure
            for page_num in range(min(5, len(doc))):
                page = doc[page_num]
                text = page.get_text()
                print(f"\nPage {page_num + 1} (first 500 chars):")
                print(text[:500])
                print("=" * 50)
            
            # Look for MMEL item patterns
            print(f"\n=== SEARCHING FOR MMEL PATTERNS IN {pdf_file} ===")
            
            patterns = [
                r'\b\d{2}-\d{2}-\d{2}\b',  # Standard Airbus format
                r'\b-\d{2}-\d{2}\b',       # Boeing format
                r'\b\d{2}-\d{2}-\d{2}-\d{2}\b',  # Extended format
                r'\b\d{2}/\d{2}/\d{2}\b',  # Slash format
                r'\b\d{2}\.\d{2}\.\d{2}\b',  # Dot format
            ]
            
            pattern_counts = {}
            sample_matches = {}
            
            for pattern in patterns:
                pattern_counts[pattern] = 0
                sample_matches[pattern] = []
            
            # Check first 20 pages for patterns
            for page_num in range(min(20, len(doc))):
                page = doc[page_num]
                text = page.get_text()
                
                for pattern in patterns:
                    matches = re.findall(pattern, text)
                    pattern_counts[pattern] += len(matches)
                    if matches and len(sample_matches[pattern]) < 5:
                        sample_matches[pattern].extend(matches[:5])
            
            print("Pattern matches found:")
            for pattern, count in pattern_counts.items():
                print(f"  {pattern}: {count} matches")
                if sample_matches[pattern]:
                    print(f"    Examples: {sample_matches[pattern][:3]}")
            
            # Look for typical MMEL content
            print(f"\n=== SEARCHING FOR MMEL CONTENT IN {pdf_file} ===")
            
            mmel_keywords = [
                "Category A", "Category B", "Category C", "Category D",
                "May be inoperative", "inoperative provided",
                "Maintenance", "Operations", "Dispatch",
                "ATA", "MMEL", "MEL"
            ]
            
            keyword_counts = {}
            for keyword in mmel_keywords:
                keyword_counts[keyword] = 0
            
            # Check first 50 pages for MMEL content
            for page_num in range(min(50, len(doc))):
                page = doc[page_num]
                text = page.get_text()
                
                for keyword in mmel_keywords:
                    keyword_counts[keyword] += text.upper().count(keyword.upper())
            
            print("MMEL keyword frequency:")
            for keyword, count in keyword_counts.items():
                print(f"  '{keyword}': {count} occurrences")
            
            # Look for item-like lines
            print(f"\n=== SEARCHING FOR ITEM-LIKE LINES IN {pdf_file} ===")
            
            item_lines = []
            for page_num in range(min(30, len(doc))):
                page = doc[page_num]
                text = page.get_text()
                lines = text.split('\n')
                
                for line in lines:
                    line = line.strip()
                    # Look for lines that might be MMEL items
                    if (len(line) > 10 and 
                        ('may be inoperative' in line.lower() or 
                         'inoperative provided' in line.lower() or
                         any(cat in line for cat in ['Category A', 'Category B', 'Category C', 'Category D']) or
                         re.search(r'\b[A-D]\b.*\d+.*\d+', line))):
                        item_lines.append(f"Page {page_num + 1}: {line[:100]}...")
                        if len(item_lines) >= 10:  # Limit output
                            break
                
                if len(item_lines) >= 10:
                    break
            
            for line in item_lines:
                print(line)
            
            doc.close()
            
        except Exception as e:
            print(f"Error analyzing {pdf_file}: {e}")
        
        print("\n" + "="*80)

if __name__ == "__main__":
    debug_b747_pdfs()
