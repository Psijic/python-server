import os
import struct
from Crypto.Cipher import AES


def encrypt_file(key, in_filename, out_filename=None, chunk_size=64 * 1024):
    """ Encrypts a file using AES (CBC mode) with the given key.
        key: The encryption key - byte object, must be either 16, 24 or 32 bytes long.
        in_filename: Name of the input file.
        out_filename: If None, '<in_filename>.enc' will be used.
        chunk_size: Size of the chunk, must be divisible by 16.
    """

    # checking params
    if not out_filename:
        out_filename = in_filename + '.enc'
    if chunk_size % 16 != 0:
        chunk_size = 64 * 1024

    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    file_size = os.path.getsize(in_filename)

    with open(in_filename, 'rb') as infile:
        with open(out_filename, 'wb') as outfile:
            outfile.write(struct.pack('<Q', file_size))
            outfile.write(iv)

            while True:
                chunk = infile.read(chunk_size)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += b' ' * (16 - len(chunk) % 16)

                outfile.write(cipher.encrypt(chunk))
    os.remove(in_filename)
    return out_filename


def decrypt_file(key, in_filename, out_filename=None, chunk_size=24 * 1024):
    # Decrypts a file using AES (CBC mode) with the given key. Parameters are similar to encrypt_file
    if not out_filename:
        out_filename = os.path.splitext(in_filename)[0]

    with open(in_filename, 'rb') as infile:
        orig_size = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
        iv = infile.read(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)

        with open(out_filename, 'wb') as outfile:
            while True:
                chunk = infile.read(chunk_size)
                if len(chunk) == 0:
                    break
                outfile.write(cipher.decrypt(chunk))

            outfile.truncate(orig_size)
    return out_filename
