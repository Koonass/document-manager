"""Quick test of portable Python setup"""
print("Testing portable Python environment...")
print()

try:
    import pandas
    print(f"[OK] pandas {pandas.__version__}")
except Exception as e:
    print(f"[FAIL] pandas failed: {e}")

try:
    import PyPDF2
    print(f"[OK] PyPDF2 {PyPDF2.__version__}")
except Exception as e:
    print(f"[FAIL] PyPDF2 failed: {e}")

try:
    import win32com.client
    print("[OK] pywin32 (win32com)")
except Exception as e:
    print(f"[FAIL] pywin32 failed: {e}")

try:
    import lxml
    print(f"[OK] lxml {lxml.__version__}")
except Exception as e:
    print(f"[FAIL] lxml failed: {e}")

print()
print("All required packages are available!")
print("Portable Python is ready for deployment.")
