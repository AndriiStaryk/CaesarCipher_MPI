import fitz
from pathlib import Path

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""

    for page in doc:
        full_text += page.get_text()

    doc.close()
    return full_text


def create_multi_page_pdf_from_text(text: str, output_path: str, font_path: str = None):
    
    doc = fitz.open()

    # Set up page parameters
    font_size = 11
    margin = 50  
    line_height = 14  
    lines_per_page = 40  
    
    text_lines = text.split("\n")
    
    # Process lines in batches for each page
    for i in range(0, len(text_lines), lines_per_page):
        
        page = doc.new_page()
        page_lines = text_lines[i:i + lines_per_page]
        
        tw = fitz.TextWriter(page.rect)
        
        font = None
        if font_path and Path(font_path).exists():
            font = fitz.Font(fontfile=font_path)
        else:
            font = fitz.Font("helv")
        
        # Calculate position for each line
        for line_num, line in enumerate(page_lines):
            y_pos = margin + line_num * line_height
            tw.append((margin, y_pos), line, font=font, fontsize=font_size)
        
        # Commit the text to the page
        tw.write_text(page)
    
    doc.save(output_path)
    doc.close()
    print(f"PDF saved as {output_path}")