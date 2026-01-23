import ctypes
from pathlib import Path

class TripleBlockCipher:
    def __init__(self):
        base_dir = Path(__file__).parent.parent
        dll_path = base_dir / "bin" / "tbc.dll"
        
        if not dll_path.exists():
            raise FileNotFoundError(f"DLL bị lạc ở đâu rồi: {dll_path}")
            
        self._lib = ctypes.CDLL(str(dll_path))
        self.__initial_args__()

    def __initial_args__(self):
        # --- Cấu trúc cho Cipher (Tầng 1 & 2) ---
        self._lib.Cipher_new.restype = ctypes.c_void_p
        self._lib.Cipher_new.argtypes = [ctypes.c_size_t]
        
        arg_types_cipher = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t, ctypes.c_float]
        self._lib.Cipher_encrypt.argtypes = arg_types_cipher
        self._lib.Cipher_decrypt.argtypes = arg_types_cipher
        self._lib.Cipher_delete.argtypes = [ctypes.c_void_p]

        # --- Cấu trúc cho EnigmaMachine (Tầng 3 - Tầng chốt chặn!) ---
        self._lib.EnigmaMachine_new.restype = ctypes.c_void_p
        self._lib.EnigmaMachine_new.argtypes = [ctypes.c_float] # Nhận float key của anh nè
        
        self._lib.EnigmaMachine_process.restype = ctypes.c_uint8
        self._lib.EnigmaMachine_process.argtypes = [ctypes.c_void_p, ctypes.c_uint8]
        
        self._lib.EnigmaMachine_delete.argtypes = [ctypes.c_void_p]

    def __process__(self, data: str | bytes, block_key: int, enigma_key: float, mode: str = "encrypt") -> bytes:
        """Hàm thực hiện mã hóa 3 tầng: 2 tầng Block + 1 tầng Enigma"""
        data_len = len(data)
        data = bytearray(data.encode()) if isinstance(data, str) else data
        mutable_data = (ctypes.c_uint8 * data_len).from_buffer_copy(data)
        
        # Khởi tạo các "cỗ máy"
        c_ptr = self._lib.Cipher_new(ctypes.c_size_t(data_len))
        e_ptr = self._lib.EnigmaMachine_new(ctypes.c_float(enigma_key))
        
        try:
            # 1. Chạy qua 2 tầng Block Cipher trước (hoặc sau tùy mode)
            # Giả sử encrypt: Block -> Enigma | decrypt: Enigma -> Block
            if mode == "encrypt":
                # Tầng 1 & 2
                self._lib.Cipher_encrypt(c_ptr, mutable_data, ctypes.c_size_t(data_len), ctypes.c_float(block_key))
                # Tầng 3 (Enigma) - Xử lý từng byte
                for i in range(data_len):
                    mutable_data[i] = self._lib.EnigmaMachine_process(e_ptr, mutable_data[i])
            else:
                # Ngược lại cho Decrypt
                for i in range(data_len):
                    mutable_data[i] = self._lib.EnigmaMachine_process(e_ptr, mutable_data[i])
                self._lib.Cipher_decrypt(c_ptr, mutable_data, ctypes.c_size_t(data_len), ctypes.c_float(block_key))
            
            return bytes(mutable_data)
        
        finally:
            # Dọn dẹp chiến trường sạch sẽ!
            self._lib.Cipher_delete(c_ptr)
            self._lib.EnigmaMachine_delete(e_ptr)

    def encrypt(self, data: str | bytes, b_key: int, e_key: float) -> str:
        return self.__process__(data, b_key, e_key, "encrypt").hex()

    def decrypt(self, data: str | bytes, b_key: int, e_key: float) -> str | bytes | None:
        decrypted : bytes = self.__process__(data, b_key, e_key, "decrypt")
        try:
            return decrypted.decode()
        except ValueError, UnicodeDecodeError:
            return decrypted