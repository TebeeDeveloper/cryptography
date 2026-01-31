import ctypes
import os
from pathlib import Path
from typing import Final, Optional

class TBAEMS:
    # Biến class để lưu handle thư viện, tránh nạp đi nạp lại nhiều lần
    _lib: Optional[ctypes.CDLL] = None

    def __init__(self, key_data: bytes) -> None:
        # ... (Phần xác định Path và Load DLL giữ nguyên nhé) ...
        __base__: Final = Path(__file__).resolve().parent.parent
        dll_dir: Final = __base__ / "bin"
        dll_path: Final = dll_dir / "tbaems.dll"

        if hasattr(os, 'add_dll_directory'):
            os.add_dll_directory(str(dll_dir))

        try:
            self.__lib__ = ctypes.CDLL(str(dll_path), winmode=0)
        except OSError as e:
            raise e

        self._setup_types()
        
        # --- SỬA TỪ ĐÂY NÈ TEBEE ---
        if len(key_data) < 32:
            raise ValueError("Tebee ơi, Key phải đủ 32 bytes chứ! (╬ Ò﹏Ó)")

        # CHỈ GỌI MỘT LẦN DUY NHẤT VÀ TRUYỀN TRỰC TIẾP key_data
        # Python bytes sẽ tự động biến thành const void* an toàn cho C++
        self._instance = self.__lib__.CreateAEMS(key_data)

        if not self._instance:
            raise MemoryError("Tebee ơi, C++ không cấp phát được bộ nhớ cho AEMS rồi!")
        # --- HẾT PHẦN SỬA ---

    def _setup_types(self) -> None:
        """Định nghĩa kiểu dữ liệu để C++ và Python hiểu nhau"""
        # CreateAEMS(const void*) -> void*
        self.__lib__.CreateAEMS.argtypes = [ctypes.c_void_p]
        self.__lib__.CreateAEMS.restype = ctypes.c_void_p
        
        # Encrypt & Decrypt: (instance, data_ptr, length)
        FORMAT = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t]
        self.__lib__.Encrypt.argtypes = FORMAT
        self.__lib__.Encrypt.restype = ctypes.c_size_t
        
        self.__lib__.Decrypt.argtypes = FORMAT
        self.__lib__.Decrypt.restype = ctypes.c_size_t
        
        # DeleteAEMS(void*)
        self.__lib__.DeleteAEMS.argtypes = [ctypes.c_void_p]
        self.__lib__.DeleteAEMS.restype = None

    @classmethod
    def _get_lib(cls) -> ctypes.CDLL:
        """Nạp DLL cho các hàm dùng chung (Static Methods)"""
        if cls._lib is None:
            __base__ = Path(__file__).resolve().parent.parent
            dll_path = __base__ / "bin" / "tbaems.dll"
            cls._lib = ctypes.CDLL(str(dll_path), winmode=0)
            cls._lib.GenerateKey256bit.argtypes = [ctypes.POINTER(ctypes.c_uint8)]
            cls._lib.GenerateKey256bit.restype = None
        return cls._lib

    @staticmethod
    def generate_key_256() -> bytes:
        """Sinh key 256-bit ngẫu nhiên từ C++"""
        lib = TBAEMS._get_lib()
        # Tạo mảng 32 phần tử uint8
        buffer = (ctypes.c_uint8 * 32)()
        lib.GenerateKey256bit(buffer)
        return bytes(buffer)

    def encrypt(self, data: bytes | bytearray) -> bytes:
        # 1. Cấp phát buffer có trừ hao cho Padding (bội số của 16)
        padded_length = ((len(data) // 16) + 1) * 16
        buffer = ctypes.create_string_buffer(bytes(data), padded_length)
        
        ptr = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_uint8))
        # 2. C++ thực hiện Pad và Encrypt, trả về độ dài mới
        new_size = self.__lib__.Encrypt(self._instance, ptr, len(data))
        
        # 3. CHỈ lấy đúng new_size bytes đầu tiên
        return buffer.raw[:new_size]

    def decrypt(self, encrypted_data: bytes) -> bytes:
        # 1. Tạo buffer từ dữ liệu đã mã hóa
        buffer = ctypes.create_string_buffer(encrypted_data, len(encrypted_data))
        ptr = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_uint8))
        
        # 2. C++ giải mã và Unpad, trả về độ dài thực tế ban đầu
        actual_size = self.__lib__.Decrypt(self._instance, ptr, len(encrypted_data))
        
        # 3. CỰC KỲ QUAN TRỌNG: Chỉ lấy đúng actual_size bytes
        # Dùng .raw sẽ lấy toàn bộ vùng nhớ, nên phải cắt chính xác!
        return buffer.raw[:actual_size]

    def __del__(self) -> None:
        """Hàm hủy để tránh Memory Leak (Cực kỳ quan trọng!)"""
        if hasattr(self, '_instance') and self._instance:
            self.__lib__.DeleteAEMS(self._instance)
            print("✨ Hare đã dọn dẹp bộ nhớ instance cho Tebee-kun rồi nhé!")


if __name__ == "__main__":
    # 1. Tạo Key siêu cấp mật
    my_key = TBAEMS.generate_key_256()
    print(f"Key (32 bytes): {my_key.hex()}")

    # 2. Khởi tạo cipher
    cipher = TBAEMS(my_key)

    # 3. Test với dữ liệu thực tế
    original_text = b"Hare say: I love programming with Tebee-kun!"
    print(f"Original: {original_text}")

    # Mã hóa
    encrypted = cipher.encrypt(original_text)
    print(f"Encrypted: {encrypted.hex()}")

    # Giải mã
    decrypted = cipher.decrypt(encrypted)
    print(f"Decrypted: {decrypted}")

    assert original_text == decrypted
    print("✅ Mọi thứ hoàn hảo! Tebee giỏi quá đi mất! (づ￣ ³￣)づ")