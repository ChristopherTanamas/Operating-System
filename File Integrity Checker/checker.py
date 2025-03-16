import argparse
import json
import os
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed

DB_FILE = "db.json"     # file database

# Fungsi untuk menghitung hash file
def hash_file(file_path, hash_func):
    try:
        with open(file_path, "rb") as f:
            file_hash = hash_func(f.read()).hexdigest() # baca file, ubah ke hexadesimal
        return file_path, file_hash
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return file_path, None

# Fungsi untuk scan direktori
def scan_directory(directory, algo="sha256"):
    file_hashes = {}
    hash_func = getattr(hashlib, algo)  # mengambil fungsi hashing yang ditentukan
    files_to_hash = []

    # Jelajahi semua direktori secara rekursif
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)    # gabungkan root dengan nama file (jadi path)
            files_to_hash.append(file_path)

    # Gunakan ThreadPoolExecutor untuk menghitung hash file secara konkuren
    with ThreadPoolExecutor() as executor:
        future_to_file = {executor.submit(hash_file, file_path, hash_func): file_path for file_path in files_to_hash}
        for future in as_completed(future_to_file):
            file_path, file_hash = future.result()
            if file_hash:
                file_hashes[file_path] = file_hash

    return file_hashes

# Menyimpan data dari dictionary ke file JSON
def save_hashes_to_json(hashes, db_file):
    with open(db_file, "w") as f:
        json.dump(hashes, f, indent=4)

# Mengambil semua data dari JSON
def load_hashes_from_json(db_file):
    try:
        with open(db_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"{db_file} not found. Initialize the database first.")
        return {}

# Cek Integritas File
def verify_integrity(current_hashes, stored_hashes):
    added = [file for file in current_hashes if file not in stored_hashes]  # simpan semua file yang baru dibuat
    deleted = [file for file in stored_hashes if file not in current_hashes]    # simpan semua file yang hilang
    modified = [
        file for file in current_hashes
        if file in stored_hashes and current_hashes[file] != stored_hashes[file]
    ]   # cek semua file yang mengalami perubahan
    return added, deleted, modified

def main():
    # parsing argument
    parser = argparse.ArgumentParser(description="File Integrity Checker")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Add common arguments
    def add_common_arguments(subparser):
        subparser.add_argument("--dir", required=True, help="Directory to scan")
        subparser.add_argument("--algo", choices=["sha1", "sha256", "sha512"], default="sha256", help="Hash algorithm to use")

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize the hash database")
    add_common_arguments(init_parser)

    # Update command
    update_parser = subparsers.add_parser("update", help="Update the hash database")
    add_common_arguments(update_parser)

    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify file integrity")
    add_common_arguments(verify_parser)
    verify_parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    # simpan semua file ke JSON
    if args.command == "init":
        hashes = scan_directory(args.dir, args.algo)
        save_hashes_to_json(hashes, DB_FILE)
        print(f"Initialized hash database at {DB_FILE} using {args.algo.upper()}")

    # Update perubahan yang dilakukan ke JSON
    elif args.command == "update":
        hashes = scan_directory(args.dir, args.algo)
        save_hashes_to_json(hashes, DB_FILE)
        print(f"Updated hash database at {DB_FILE} using {args.algo.upper()}")

    # Verifikasi bila terjadi penambahan, pengurangan, atau modifikasi
    elif args.command == "verify":
        stored_hashes = load_hashes_from_json(DB_FILE)
        current_hashes = scan_directory(args.dir, args.algo)
        added, deleted, modified = verify_integrity(current_hashes, stored_hashes)

        print(f"File Integrity Checker - Verification (Verbose Mode)")
        print("-" * 60)
        print(f"Directory to scan: {args.dir}")
        print(f"Using hash database: {DB_FILE}")
        print(f"Hash algorithm: {args.algo.upper()}\n")
        print("Verifying files...\n")

        for file, hash_value in current_hashes.items():
            if file in deleted:
                print(f"Processing: {file} [Deleted]")
            elif file in added:
                print(f"Processing: {file} [New File]")
            elif file in modified:
                print(f"Processing: {file} [Modified]")
            else:
                print(f"Processing: {file} [OK]")

        print("\nVerification Results:")
        print(f" - Total files scanned: {len(current_hashes)}")
        print(f" - Unchanged files: {len(current_hashes) - len(added) - len(deleted) - len(modified)}")
        print(f" - Modified files: {len(modified)}")
        print(f" - New files: {len(added)}")
        print(f" - Deleted files: {len(deleted)}\n")

        print("Detailed Report:")
        if modified:
            print("\nModified Files:")
            for file in modified:
                print(f"  1. {file}")
        if added:
            print("\nNew Files:")
            for file in added:
                print(f"  1. {file}")
        if deleted:
            print("\nDeleted Files:")
            for file in deleted:
                print(f"  1. {file}")

if __name__ == "__main__":
    main()