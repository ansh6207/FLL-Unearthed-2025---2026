#!/usr/bin/env python3
import zipfile
import os

os.chdir(r"c:\Users\aarya\code\FLL-Unearthed-2025---2026")

# Create LLSP3 file (ZIP archive)
with zipfile.ZipFile("test.llsp3", "w") as llsp3:
    llsp3.write("projectbody.json", "projectbody.json")

print("Created test.llsp3")
os.remove("projectbody.json")
print("Cleaned up temporary files")
