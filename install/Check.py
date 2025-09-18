import sys

def check_library(library_name):
    try:
        __import__(library_name)
        print(f"✅ {library_name} đã được cài đặt")
        return True
    except ImportError:
        print(f"❌ {library_name} chưa được cài đặt")
        return False

def main():
    print("KIỂM TRA THƯ VIỆN CẦN THIẾT")
    print("=" * 40)
    
    # Danh sách các thư viện cần kiểm tra
    required_libraries = ['requests', 'pandas', 'openpyxl']
    
    all_installed = True
    for lib in required_libraries:
        if not check_library(lib):
            all_installed = False
    
    print("=" * 40)
    if all_installed:
        print(">>>  All Libraries Installed  <<<")
    else:
        print("Library not installed...!!!!!!!!!!!!!!!!!")
    # Chờ nhấn Enter trước khi thoát
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()