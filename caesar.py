# _-_-_-_-_-_-_-_-_-_-_-_- Caesar Cipher _-_-_-_-_-_-_-_-_-_-_-_-


alphabet_upper = "АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ"
alphabet_lower = alphabet_upper.lower()
alphabet_len = len(alphabet_upper)

def caesar_shift(char, shift): 
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
