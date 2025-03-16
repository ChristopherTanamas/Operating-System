# Importing libraries
import os
import threading
from concurrent.futures import ThreadPoolExecutor
import re

# Lock untuk sinkronisasi akses ke shared_list
lock = threading.Lock()
shared_list = []

def search_txt(file_paths, keyword, thread_info=None):
    for file_path in file_paths:
        try:
            #Cek keyword is a regular expression or not
            try:
                regex = re.compile(keyword)
                is_regex = True
            except re.error:
                is_regex = False

            #Mendapatkan info thread
            if thread_info:
                thread_info()

            with open(file_path, "r", encoding='utf-8') as file:
                full_text = file.read()

            # Lewati file kosong
            if full_text.strip() == "":
                continue
            
            # Jika keyword ditemukan dalam teks, hitung jumlah kemunculannya
            if is_regex:
                count = len(re.findall(regex, full_text))
            elif keyword in full_text:
                count = full_text.count(keyword)

            # Gunakan lock untuk mengakses shared_list secara aman
            with lock:
                if count > 0:
                    shared_list.append((file_path, count))
                    
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

# Fungsi untuk membagi file menjadi batch untuk setiap thread
def divide_batch(all_file_list, max_threads):
    # Hitung jumlah file per thread (agar rata)
    batch_size = len(all_file_list) // max_threads
    batch = []
    for i in range(0, len(all_file_list), batch_size):
        batch.append(all_file_list[i:i + batch_size])
    return batch

# Mencari file di sub directory (recursively)
def sub_directory_search(directory_path):
    text_files = []
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.txt'):
                text_files.append(os.path.join(root, file))
    return text_files

def search_keyword_in_files(directory_path, keyword, max_threads, thread_info=None):
    try:
        all_file_list = sub_directory_search(directory_path)  # Temukan semua file teks secara rekursif

        # Kalau tidak ada file, return
        if not all_file_list:
            print("No text files found in the directory.")
            return

        batch_file = divide_batch(all_file_list, max_threads) # Bagi file ke dalam batch sesuai dengan jumlah thread

        # Mulai pencarian dengan menggunakan ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            # Bagikan pekerjaan ke thread pool
            executor.map(lambda x: search_txt(x, keyword, thread_info), batch_file)

    except FileNotFoundError:
        print(f"Error: The directory {directory_path} does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

def main(directory_path, keyword, max_threads, thread_info=None):
    search_keyword_in_files(directory_path, keyword, max_threads, thread_info)
    
    if shared_list:
        print("\nFiles containing the keyword:")
        for file_path, count in shared_list:
            print(f"{file_path} - Occurrences: {count}")
    else:
        print("No files contain the keyword.")
    
    return shared_list

if __name__ == "__main__":
    directory_path = input("Enter the directory path: ")
    keyword = input("Enter the keyword to search for: ")
    result= main(directory_path, keyword, 4)