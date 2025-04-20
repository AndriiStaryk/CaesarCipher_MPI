from mpi4py import MPI
from pdf_manager import extract_text_from_pdf, create_multi_page_pdf_from_text

# _-_-_-_-_-_-_-_-_-_-_-_- Caesar Cipher _-_-_-_-_-_-_-_-_-_-_-_-
alphabet_upper = "АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ"
alphabet_lower = alphabet_upper.lower()
alphabet_len = len(alphabet_upper)

def caesar_shift(text, shift):
    for char in text:
        if char in alphabet_upper:
            index = alphabet_upper.index(char)
            new_index = (index + shift) % alphabet_len
            return alphabet_upper[new_index]
        elif char in alphabet_lower:
            index = alphabet_lower.index(char)
            new_index = (index + shift) % alphabet_len
            return alphabet_lower[new_index]
        else:
            return char
        
def caesar_encrypt(text_chunk, shift):
    return ''.join(caesar_shift(char, shift) for char in text_chunk)

# _-_-_-_-_-_-_-_-_-_-_-_- MPI Setup _-_-_-_-_-_-_-_-_-_-_-_-
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Only the main process enters the text
if rank == 0:
    text = extract_text_from_pdf("cipher_test.pdf")
    shift = 33

    # Divide the text into equal parts
    chunk_size = len(text) // size
    chunks = [text[i*chunk_size : (i+1)*chunk_size] for i in range(size)]

    # The last process gets the remainder
    if len(text) % size != 0:
        chunks[-1] += text[size*chunk_size:]
else:
    chunks = None
    shift = None

shift = comm.bcast(shift, root=0)                   # Broadcast the shift value to all processes
chunk = comm.scatter(chunks, root=0)                # Scatter text chunks to all processes
encrypted_chunk = caesar_encrypt(chunk, shift)      # Each process encrypts its own chunk
gathered = comm.gather(encrypted_chunk, root=0)     # Gather the encrypted results

if rank == 0:
    encrypted_text = ''.join(gathered)
    create_multi_page_pdf_from_text(encrypted_text, "encrypted_text.pdf", "e-Ukraine-Medium.otf")
