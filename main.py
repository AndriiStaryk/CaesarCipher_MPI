from mpi4py import MPI
from caesar import caesar_encrypt
from pdf_manager import extract_text_from_pdf_parallel, create_pdf_from_text_chunk, merge_pdfs
import fitz
import math
import time
import os

# _-_-_-_-_-_-_-_-_-_-_-_- MPI Setup _-_-_-_-_-_-_-_-_-_-_-_-
start_time = time.time()

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

input_pdf = "harry_potter_merged.pdf"
output_pdf = "encrypted_text.pdf"
font_path = "e-Ukraine-Medium.otf"
shift = 33

# Get document info
if rank == 0:
    doc = fitz.open(input_pdf)
    page_count = doc.page_count
    doc.close()
else:
    page_count = None

# Broadcast page count and shift to all processes
page_count = comm.bcast(page_count, root=0)
shift = comm.bcast(shift, root=0)

# Divide PDF pages among processes
pages_per_process = math.ceil(page_count / size)
start_page = rank * pages_per_process
end_page = min((rank + 1) * pages_per_process, page_count)

# Each process reads its portion of the PDF
io_start_time = time.time()
text_chunk = extract_text_from_pdf_parallel(input_pdf, start_page, end_page)
io_read_time = time.time() - io_start_time

# Each process encrypts its text chunk
encryption_start_time = time.time()
encrypted_chunk = caesar_encrypt(text_chunk, shift)
encryption_time = time.time() - encryption_start_time

# Each process creates its own PDF portion
temp_pdf_path = f"temp_encrypted_{rank}.pdf"
io_write_start_time = time.time()
pages_created = create_pdf_from_text_chunk(encrypted_chunk, temp_pdf_path, start_page, font_path)
io_write_time = time.time() - io_write_start_time

# Collect timing stats from all processes
timing_data = comm.gather((io_read_time, encryption_time, io_write_time, pages_created), root=0)

# Master process merges all PDFs
if rank == 0:
    merge_start_time = time.time()
    
    # Create list of all temporary PDFs
    temp_pdfs = [f"temp_encrypted_{i}.pdf" for i in range(size)]
    
    # Merge them
    merge_pdfs(temp_pdfs, output_pdf)
    merge_time = time.time() - merge_start_time
    
    # Remove temporary files
    for pdf in temp_pdfs:
        try:
            os.remove(pdf)
        except:
            pass
    
    # Print timing statistics
    total_time = time.time() - start_time
    total_read_time = sum(t[0] for t in timing_data)
    total_encryption_time = sum(t[1] for t in timing_data)
    total_write_time = sum(t[2] for t in timing_data)
    total_pages = sum(t[3] for t in timing_data)
    
    print(f"PDF successfully encrypted and saved as {output_pdf}")
    print(f"Total pages: {total_pages}")
    print(f"Average read time per process: {total_read_time/size:.3f} seconds")
    print(f"Average encryption time per process: {total_encryption_time/size:.3f} seconds")
    print(f"Average write time per process: {total_write_time/size:.3f} seconds")
    print(f"Merge time: {merge_time:.3f} seconds")
    print(f"Total execution time: {total_time:.3f} seconds")