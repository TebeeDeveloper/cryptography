import ctypes
import os
from pathlib import Path
from typing import Final

class TebeeFastStreamCipher:
    def __init__(self) -> None:
        self.__BASE_DIR__: Final = Path(__file__).parent.parent
        # Chỉnh lại đường dẫn chuẩn theo cấu trúc của anh
        self.__DLL_PATH__: Final = self.__BASE_DIR__ / "bin" / "tfsc.dll"
        
        if not self.__DLL_PATH__.exists():
            raise FileNotFoundError(f"Không thấy DLL tại: {self.__DLL_PATH__}")
            
        self.__lib__ = ctypes.CDLL(str(self.__DLL_PATH__))
        self.__initial_args__()

    def __initial_args__(self) -> None:
        # Cấu trúc: void tfsc_encrypt(uint8_t* data, size_t len, uint8_t* key)
        common_args = [
            ctypes.POINTER(ctypes.c_uint8), # Data
            ctypes.c_size_t,               # Len
            ctypes.POINTER(ctypes.c_uint8)  # Key (128 bytes)
        ]
        
        self.__lib__.tfsc_encrypt.argtypes = common_args
        self.__lib__.tfsc_encrypt.restype = None
        
        self.__lib__.tfsc_decrypt.argtypes = common_args
        self.__lib__.tfsc_decrypt.restype = None

    def to_byte(self, data: str) -> bytearray:
        return bytearray(data.encode('utf-8'))

    def encrypt(self, data: bytearray, key: bytes) -> None:
        if not isinstance(data, bytearray):
            raise TypeError("Data phải là bytearray nha!")
        
        # 1. Padding PKCS#7
        orig_len = len(data)
        pad_needed = 16 - (orig_len % 16)
        data.extend([pad_needed] * pad_needed)

        # 2. Gọi C++ thông qua hàm con để giải phóng pointer ngay
        def _execute():
            # Tạo pointer cho data
            data_ptr = (ctypes.c_uint8 * len(data)).from_buffer(data)
            # Tạo pointer cho key (chỉ đọc)
            key_ptr = (ctypes.c_uint8 * 128).from_buffer_copy(key)
            
            self.__lib__.tfsc_encrypt(
                ctypes.cast(data_ptr, ctypes.POINTER(ctypes.c_uint8)),
                ctypes.c_size_t(len(data)),
                ctypes.cast(key_ptr, ctypes.POINTER(ctypes.c_uint8))
            )
        
        _execute()

    def decrypt(self, data: bytearray, key: bytes) -> None:
        if not data or len(data) % 16 != 0: return

        def _execute():
            data_ptr = (ctypes.c_uint8 * len(data)).from_buffer(data)
            key_ptr = (ctypes.c_uint8 * 128).from_buffer_copy(key)
            
            self.__lib__.tfsc_decrypt(
                ctypes.cast(data_ptr, ctypes.POINTER(ctypes.c_uint8)),
                ctypes.c_size_t(len(data)),
                ctypes.cast(key_ptr, ctypes.POINTER(ctypes.c_uint8))
            )
        
        _execute()

        pad_val = data[-1]
        # Unpadding
        if 0 < pad_val <= 16:
            # Chỉ lấy phần dữ liệu xịn, bỏ phần padding
            clean_data = data[:-pad_val]
        else:
            clean_data = data

        # Trả về chuỗi string đã decode
        return clean_data.decode('utf-8', errors='ignore')