# -*- coding: utf-8 -*-
"""
Python port of igapack.pas (Innocent Grey Archive Unpacker/Packer)
Original by RikuKH3.

This script can unpack and pack .iga archive files from Innocent Grey games.
"""

import sys
import os
import struct
import io

#关键函数：Multibyte 读写
def get_multibyte(f: io.BytesIO) -> int:
    """
    Reads a custom variable-length integer from the file stream.

    This is a 7-bit encoding. It reads bytes until it finds one
    where the least significant bit (LSB) is 1.
    All 7-bit payloads are combined and the whole thing is
    right-shifted by 1 to get the final value.
    """
    result = 0
    while (result & 1) == 0:
        byte1 = f.read(1)
        if not byte1:
            #Handle unexpected end of file
            if result == 0:
                return -1  # Or raise error
            break
        byte1_val = byte1[0]
        result = (result << 7) | byte1_val
    return result >> 1


def enc_multibyte(f: io.BytesIO, value: int):
    """
    Writes an integer as a custom variable-length integer.

    This is the reverse of get_multibyte. It left-shifts the value
    by 1, then writes it out in 7-bit chunks. All chunks have
    LSB=0 except for the last one, which has LSB=1.
    """
    value = value << 1

    to_write = []

    #These conditions check if the value is large enough to need
    #multi-byte chunks, writing them from most-significant to least.
    if (value >> 28) > 1:
        to_write.append(((value >> 29) << 1) & 0xFF)
    if (value >> 21) > 1:
        to_write.append(((value >> 22) << 1) & 0xFF)
    if (value >> 14) > 1:
        to_write.append(((value >> 15) << 1) & 0xFF)
    if (value >> 7) > 1:
        to_write.append(((value >> 8) << 1) & 0xFF)

    #The final byte contains the last 7 bits of data, with LSB set to 1
    #to signify the end of the number.
    to_write.append((value & 0x7F) | 1)  # Corrected: only use 7 bits (0x7F)

    #Wait, the Pascal logic is `Byte1:=Byte(LongWord1) or 1;`
    #this implies it uses the full 8 bits (0xFF) for the last byte.
    #Let's re-test the original logic from Pascal.
    to_write_pascal = []
    if (value >> 28) > 1:
        to_write_pascal.append(((value >> 29) << 1) & 0xFF)
    if (value >> 21) > 1:
        to_write_pascal.append(((value >> 22) << 1) & 0xFF)
    if (value >> 14) > 1:
        to_write_pascal.append(((value >> 15) << 1) & 0xFF)
    if (value >> 7) > 1:
        to_write_pascal.append(((value >> 8) << 1) & 0xFF)

    #Pascal: `Byte1:=Byte(LongWord1) or 1;`
    #This uses the LSB 8 bits of the value and sets LSB to 1.
    to_write_pascal.append((value & 0xFF) | 1)

    f.write(bytes(to_write_pascal))

#核心解密函数
def decrypt_data(data: bytearray) -> bytearray:
    """
    Decrypts the file data using a simple XOR cipher.
    Each byte is XORed with (index + 2).
    """
    for i in range(len(data)):
        data[i] ^= (i + 2) & 0xFF
    return data

def encrypt_data(data: bytearray) -> bytearray:
    """
    Encrypts the file data using the same simple XOR cipher.
    """
    # XOR is symmetrical, so encryption is the same as decryption.
    return decrypt_data(data)

#解包 (Unpack)
def unpack(input_file: str):
    """
    Unpacks an .iga archive.
    """
    print(f"Unpacking {input_file}...")
    #Create output directory based on the input file name (without .iga)
    output_dir = os.path.splitext(input_file)[0]
    os.makedirs(output_dir, exist_ok=True)

    file_list = []

    with open(input_file, 'rb') as f:
        #1. Read and check header
        magic = f.read(4)
        if magic != b'IGA0':
            print("Error: Input file is not a valid Innocent Grey Archive file.")
            return

        #Read the archive ID (e.g., [2])
        archive_id = struct.unpack('<I', f.read(4))[0]
        file_list.append(f"[{archive_id}]")

        #Skip unknown header bytes
        f.seek(0x10)

        #2. Read Entry Table
        #This table contains (FilenamePos, DataPos, DataSize)
        entry_table_len = get_multibyte(f)
        entry_table_data = io.BytesIO(f.read(entry_table_len))

        clean_lut = []  #A "clean" lookup table
        while entry_table_data.tell() < entry_table_len:
            filename_pos = get_multibyte(entry_table_data)
            data_pos = get_multibyte(entry_table_data)
            data_size = get_multibyte(entry_table_data)
            if filename_pos == -1: break  # Check for EOF
            clean_lut.append({
                'pos': filename_pos,
                'data_pos': data_pos,
                'size': data_size
            })

        file_count = len(clean_lut)
        print(f"Found {file_count} files.")

        #3. Read Filename Block
        filenames_len = get_multibyte(f)
        #Calculate the absolute start position of the file data block
        data_block_pos = f.tell() + filenames_len
        filenames_data = io.BytesIO(f.read(filenames_len))

        #4. Extract all files
        for i in range(file_count):
            entry = clean_lut[i]
            filename_pos = entry['pos']
            data_pos = entry['data_pos']
            data_size = entry['size']

            #Determine where this filename ends by looking at the *next*
            #file's starting position.
            if i + 1 < file_count:
                filename_end = clean_lut[i + 1]['pos']
            else:
                #This is the last file, so its name runs to the end
                filename_end = filenames_len

            #Seek to the start of the filename string
            filenames_data.seek(filename_pos)

            #Read the filename. Filenames are stored as a sequence of
            #multibyte-encoded character codes.
            s = ""
            while filenames_data.tell() < filename_end:
                char_code = get_multibyte(filenames_data)
                s += chr(char_code)

            file_list.append(s)

            #5. Read and Decrypt File Data
            #Seek the main file to the file's data location
            f.seek(data_block_pos + data_pos)
            encrypted_data = bytearray(f.read(data_size))

            #Decrypt the data
            decrypted_data = decrypt_data(encrypted_data)

            #6. Save the decrypted file
            #Ensure subdirectory exists if filename contains paths
            output_filename = os.path.join(output_dir, s)
            output_file_dir = os.path.dirname(output_filename)
            if output_file_dir:
                os.makedirs(output_file_dir, exist_ok=True)

            with open(output_filename, 'wb') as out_f:
                out_f.write(decrypted_data)

            #Update progress
            print(f"[{i + 1:04d}/{file_count:04d}] {s}")

        #7. Save the file list
        list_path = os.path.join(output_dir, 'iga_filelist.txt')
        with open(list_path, 'w', encoding='utf-8') as flist_f:
            flist_f.write("\n".join(file_list))

        print(f"Unpack complete. Files are in '{output_dir}'")
        print(f"File list saved to '{list_path}'")

#封包 (Pack)
def pack(input_dir: str):
    """
    Packs a directory back into an .iga archive.
    """
    print(f"Packing {input_dir}...")

    #1. Find and read the file list
    file_list_path = os.path.join(input_dir, 'iga_filelist.txt')
    if not os.path.exists(file_list_path):
        print(f"Error: 'iga_filelist.txt' not found in '{input_dir}'")
        return

    output_file = input_dir.rstrip('/\\') + '.iga'

    with open(file_list_path, 'r', encoding='utf-8') as f:
        # Read all lines, stripping newline characters
        lines = [line.strip() for line in f.readlines() if line.strip()]

    #First line is the archive ID, e.g., [2]
    archive_id = int(lines[0].strip('[]'))
    #The rest are the filenames
    filenames = lines[1:]
    file_count = len(filenames)

    print(f"Found {file_count} files to pack.")

    #We will write to in-memory streams first
    entry_table = io.BytesIO()
    filename_block = io.BytesIO()
    data_blobs = []  # Store encrypted file data here

    filename_pos = 0  # This will be the byte offset in filename_block
    data_pos = 0  # This will be the byte offset in the data block

    #2. Process all files
    for i, s in enumerate(filenames):
        print(f"[{i + 1:04d}/{file_count:04d}] {s}")

        #Filename Block
        # Current position is the start of this filename
        filename_start_pos = filename_block.tell()
        # Encode the filename string using multibyte for each char
        for char in s:
            enc_multibyte(filename_block, ord(char))

        #Data Block
        file_path = os.path.join(input_dir, s)
        if not os.path.exists(file_path):
            print(f"Warning: File not found, skipping: {s}")
            data_size = 0
            data_blobs.append(b"")  # Append empty data
        else:
            with open(file_path, 'rb') as f_in:
                decrypted_data = bytearray(f_in.read())

            data_size = len(decrypted_data)

            # Encrypt the data
            encrypted_data = encrypt_data(decrypted_data)
            data_blobs.append(encrypted_data)

        #Entry Table
        #Write the 3-part entry for this file
        enc_multibyte(entry_table, filename_start_pos)
        enc_multibyte(entry_table, data_pos)
        enc_multibyte(entry_table, data_size)

        #Update total data position for the next file
        data_pos += data_size

    #3. Get final byte chunks
    entry_table_bytes = entry_table.getvalue()
    filename_block_bytes = filename_block.getvalue()

    #4. Write the final .iga file
    with open(output_file, 'wb') as f_out:
        # Write header
        f_out.write(b'IGA0')
        f_out.write(struct.pack('<I', archive_id))
        f_out.write(struct.pack('<I', 2))  # Constant 0x00000002
        f_out.write(struct.pack('<I', 2))  # Constant 0x00000002

        # Write Entry Table Length and Data
        enc_multibyte(f_out, len(entry_table_bytes))
        f_out.write(entry_table_bytes)

        # Write Filename Block Length and Data
        enc_multibyte(f_out, len(filename_block_bytes))
        f_out.write(filename_block_bytes)

        # Write all the encrypted file data blobs
        for blob in data_blobs:
            f_out.write(blob)

    print(f"Pack complete. Output file: '{output_file}'")

# 主程序入口
def main():
    """
    Main entry point.
    Parses command-line arguments and calls unpack or pack.
    """
    print("Innocent Grey Archive Unpacker/Packer (Python Port)")
    print("-----------------------------------------------------")

    # Check if we have at least one argument (the script name + input)
    if len(sys.argv) < 2:
        print("Usage: python igapack.py [file.iga | folder]")
        print("\n- To Unpack: Drag and drop an .iga file onto this script")
        print("             or run: python igapack.py your_file.iga")
        print("\n- To Pack:   Drag and drop a folder (containing iga_filelist.txt)")
        print("           or run: python igapack.py your_folder")
        sys.exit(1)

    input_path = sys.argv[1]

    try:
        #Check if the input is a file ending in .iga
        if os.path.isfile(input_path) and input_path.lower().endswith('.iga'):
            unpack(input_path)
        #Check if the input is a directory
        elif os.path.isdir(input_path):
            pack(input_path)
        else:
            print(f"Error: Not a valid .iga file or folder: {input_path}")
            sys.exit(1)

    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()