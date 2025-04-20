import fitz
from pathlib import Path

def extract_text_from_pdf_parallel(pdf_path, start_page, end_page):
    """Extract text from a specific range of pages in a PDF"""
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(start_page, min(end_page, doc.page_count)):
        text += doc[page_num].get_text()
    doc.close()
    return text


def create_pdf_from_text_chunk(text, output_path, font_path=None):
    """Create a PDF with a chunk of text starting at page_start_num"""
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
    return len(text_lines) // lines_per_page + (1 if len(text_lines) % lines_per_page > 0 else 0)  # Return number of pages created

def merge_pdfs(input_paths, output_path):
    """Merge multiple PDF files into one"""
    result = fitz.open()
    for pdf_path in input_paths:
        with fitz.open(pdf_path) as pdf:
            result.insert_pdf(pdf)
    result.save(output_path)
    result.close()