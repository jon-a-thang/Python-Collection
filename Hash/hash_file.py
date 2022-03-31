"""
Filename:
    hash_file.py

Description:
    This program will return the hash of a file

Author(s):
    Jonathan Jang
"""
import hashlib


def hash_file(filename1):
    # Use hashlib to store the hash of a file
    #   Examples:
    #       Use .sha1() or .sha256(), or .md5(), or .sha3_256()
    h1 = hashlib.sha3_256()

    with open(filename1, "rb") as file:

        # Use file.read() to read the size of file
        # and read the file in small chunks
        # because we cannot read the large files.
        chunk = 0
        while chunk != b'':
            chunk = file.read(1024)
            h1.update(chunk)

        # hexdigest() is of 160 bits
        return h1.hexdigest()


if __name__ == '__main__':
    hash_file("ENTER_FILEPATH_OF_FILE_NAME_TO_HASH")
