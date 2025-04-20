from mpi4py import MPI
from caesar import caesar_encrypt
from pdf_manager import extract_text_from_pdf, create_multi_page_pdf_from_text
import time


# _-_-_-_-_-_-_-_-_-_-_-_- MPI Setup _-_-_-_-_-_-_-_-_-_-_-_-

start_time = time.time()

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Only the main process enters the text
if rank == 0:
    text = extract_text_from_pdf("harry_potter_merged.pdf")
    shift = 12

    # Divide the text into equal parts
    chunk_size = len(text) // size
    chunks = [text[i*chunk_size : (i+1)*chunk_size] for i in range(size)]

    # The last process gets the remainder
    if len(text) % size != 0:
        chunks[-1] += text[size*chunk_size:]
else:
    chunks = None
    shift = None

encryption_start_time = time.time()

shift = comm.bcast(shift, root=0)                   # Broadcast the shift value to all processes
chunk = comm.scatter(chunks, root=0)                # Scatter text chunks to all processes
encrypted_chunk = caesar_encrypt(chunk, shift)      # Each process encrypts its own chunk
gathered = comm.gather(encrypted_chunk, root=0)     # Gather the encrypted results

encryption_end_time = time.time()
encryption_time_taken = encryption_end_time - encryption_start_time

if rank == 0:
    encrypted_text = ''.join(gathered)
    print(f"Encryption time taken: {encryption_time_taken} seconds")
    create_multi_page_pdf_from_text(encrypted_text, "encrypted_text.pdf", "e-Ukraine-Medium.otf")
    total_time_taken = time.time() - start_time
    print(f"Total time taken: {total_time_taken} seconds")
