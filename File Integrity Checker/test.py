import unittest
import os
import json
from checker import scan_directory, save_hashes_to_json, load_hashes_from_json, verify_integrity, DB_FILE

class TestFileIntegrityChecker(unittest.TestCase):
    # Setup setiap kali test dimulai (membuat dummy directory dan file)
    def setUp(self):
        self.test_dir = "test_dir"
        os.makedirs(self.test_dir, exist_ok=True)
        self.test_file = os.path.join(self.test_dir, "test_file.txt")
        with open(self.test_file, "w") as f:
            f.write("This is a test file.")

    # Setup setiap kali test dimulai (delete file dari test sebelumnya)
    def tearDown(self):
        if os.path.exists(self.test_dir):
            for root, _, files in os.walk(self.test_dir, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                os.rmdir(root)
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)

    # Test file ada di hash
    def test_scan_directory_sha1(self):
        self._test_scan_directory("sha1")

    def test_scan_directory_sha256(self):
        self._test_scan_directory("sha256")

    def test_scan_directory_sha512(self):
        self._test_scan_directory("sha512")

    def _test_scan_directory(self, algo):
        hashes = scan_directory(self.test_dir, algo)
        self.assertIn(self.test_file, hashes)

    # Test save dan load hash
    def test_save_and_load_hashes_sha1(self):
        self._test_save_and_load_hashes("sha1")

    def test_save_and_load_hashes_sha256(self):
        self._test_save_and_load_hashes("sha256")

    def test_save_and_load_hashes_sha512(self):
        self._test_save_and_load_hashes("sha512")

    def _test_save_and_load_hashes(self, algo):
        hashes = scan_directory(self.test_dir, algo)
        save_hashes_to_json(hashes, DB_FILE)
        loaded_hashes = load_hashes_from_json(DB_FILE)
        self.assertEqual(hashes, loaded_hashes)

    #Test verify integrity
    def test_verify_integrity_sha1(self):
        self._test_verify_integrity("sha1")

    def test_verify_integrity_sha256(self):
        self._test_verify_integrity("sha256")

    def test_verify_integrity_sha512(self):
        self._test_verify_integrity("sha512")

    def _test_verify_integrity(self, algo):
        # Tidak ada modify
        initial_hashes = scan_directory(self.test_dir, algo)
        save_hashes_to_json(initial_hashes, DB_FILE)
        current_hashes = scan_directory(self.test_dir, algo)
        added, deleted, modified = verify_integrity(current_hashes, initial_hashes)
        self.assertEqual(len(added), 0)
        self.assertEqual(len(deleted), 0)
        self.assertEqual(len(modified), 0)
        
        # Jika ada yang sudah dimodify
        with open(self.test_file, "w") as f:
            f.write("This file has been modified.")
        current_hashes = scan_directory(self.test_dir, algo)
        added, deleted, modified = verify_integrity(current_hashes, initial_hashes)
        self.assertEqual(len(modified), 1)
        self.assertIn(self.test_file, modified)

if __name__ == "__main__":
    unittest.main()