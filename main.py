from mpi4py import MPI

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

# --- MPI setup ---
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Тільки головний процес вводить текст
if rank == 0:
    text = "Привіт, як справи? Це тест шифру Цезаря для української мови!"
    shift = 3

    # Ділимо текст на рівні частини
    chunk_size = len(text) // size
    chunks = [text[i*chunk_size : (i+1)*chunk_size] for i in range(size)]

    # останній процес отримає залишок
    if len(text) % size != 0:
        chunks[-1] += text[size*chunk_size:]
else:
    chunks = None
    shift = None


shift = comm.bcast(shift, root=0)                   # Розсилка зсуву всім процесам
chunk = comm.scatter(chunks, root=0)                # Розсилка частин тексту всім процесам
encrypted_chunk = caesar_encrypt(chunk, shift)      # Кожен процес шифрує свою частину
gathered = comm.gather(encrypted_chunk, root=0)     # Збір результатів

if rank == 0:
    encrypted_text = ''.join(gathered)
    print("Зашифровано:", encrypted_text)