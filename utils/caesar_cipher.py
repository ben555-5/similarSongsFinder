SHIFT_DEFAULT = 10

def caesar_encrypt(text, shift=SHIFT_DEFAULT):
    result = ""
    if not text:
        return result
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            # shift and wrap around the alphabet
            result += chr((ord(char) - base + shift) % 26 + base)
        else:
            result += char  # keep spaces/punctuation unchanged
    return result

def caesar_decrypt(text, shift=SHIFT_DEFAULT):
    return caesar_encrypt(text, -shift)
