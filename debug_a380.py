import fitz  # PyMuPDF
import re

def analyze_a380_pdf():
    """Analyze A380 PDF structure to understand parsing issues"""
    
    pdf_path = "A-380 R0.pdf"
    
    try:
        doc = fitz.open(pdf_path)
        print(f"=== A380 PDF ANALYSIS ===")
        print(f"Total pages: {len(doc)}")
        print()
        
        # Check first few pages for structure
        for page_num in range(min(5, len(doc))):
            page = doc[page_num]
            text = page.get_text()
            print(f"Page {page_num + 1} (first 500 chars):")
            print(text[:500])
            print("=" * 50)
            
        # Look for MMEL item patterns across several pages
        print("\n=== SEARCHING FOR MMEL PATTERNS ===")
        
        # Different patterns to try
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
        print("\n=== SEARCHING FOR MMEL CONTENT ===")
        
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
        
        # Check for table of contents or index
        print("\n=== CHECKING FOR TABLE OF CONTENTS ===")
        
        toc_keywords = ["Contents", "Index", "Table of Contents", "Chapter"]
        
        for page_num in range(min(10, len(doc))):
            page = doc[page_num]
            text = page.get_text()
            
            for keyword in toc_keywords:
                if keyword.upper() in text.upper():
                    print(f"Found '{keyword}' on page {page_num + 1}")
                    # Show some context
                    lines = text.split('\n')
                    for i, line in enumerate(lines):
                        if keyword.upper() in line.upper():
                            start = max(0, i-2)
                            end = min(len(lines), i+3)
                            print(f"  Context: {lines[start:end]}")
                            break
        
        doc.close()
        
    except Exception as e:
        print(f"Error analyzing A380 PDF: {e}")
        return False
    
    return True

if __name__ == "__main__":
    analyze_a380_pdf()
