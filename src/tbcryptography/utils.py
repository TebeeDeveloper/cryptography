from tbcryptography import atbash, caesar, EnigmaMachine, vigenere, tbc, tfsc
from base64 import b85encode, b85decode
import os

def atbash_mc() -> None:
    while True:
        msg = input("Nhập tin nhãn của bạn:\n>>>>")
        if msg == "quit()":
            return None
        print(atbash.process(msg))

def caesar_mc() -> None:
    while True:
        msg = input("Nhập tin nhắn của bạn:\n>>>>")
        if msg == "quit()":
            return None
        shift = input("Nhập số dịch chuyển của bạn:\n>>>>")
        print(caesar.process(msg, shift))

def enigma_mc() -> None:
    while True:
        seed = input("Nhập seed của bạn: ")
        if seed == "quit()":
            return None
        seed = eval(seed)
        if not isinstance(seed, int):
            continue
        enigma = EnigmaMachine(seed)
        mode = input("Nhập chế độ (encrypt/decrypt): ")
        msg = input("Nhập tin nhắn của bạn:\n>>>>")
        if mode == "encrypt":
            print(enigma.process_text(b85encode(msg.encode()).decode()))
        else:
            print(b85decode(enigma.process_text))

def vigenere_mc() -> None:
    while True:
        mode = input("Nhập chế độ (encrypt/decrypt): ")
        if mode == "quit()":
            return None
        msg = input("Nhập tin nhắn của bạn:\n>>>>")
        key = input("Nhập khóa của bạn:\n>>>>")
        if mode == "encrypt":
            print(vigenere.encrypt(msg, key))
        else:
            print(vigenere.decrypt(msg, key))

def tbc_mc() -> None:
    while True:
        mode = input("Nhập chế độ (encrypt/decrypt): ")
        msg = input("Nhập tin nhắn của bạn:\n>>>>")
        key = eval(input("Nhập khóa của bạn:\n>>>>"))
        if mode == "encrypt":
            print(tbc.encrypt(msg, key, key))
        else:
            print(tbc.decrypt(msg, key, key))

def tfsc_mc() -> None:
    while True:
        mode = input("Nhập chế độ (encrypt/decrypt): ")
        if mode == "quit()":
            return None
        key = input("Nhập khóa (random/mykey): ")
        if key == "quit()":
            return None
        if key == "mykey":
            key = input("Nhập khóa:\n>>>> ")
        if key == "random":
            key = os.urandom(128)
        msg = bytearray(input("Nhập tin nhắn của bạn:\n>>>> ").encode())
        if mode == "encrypt":
            tfsc.encrypt(msg, key)
            print(key)
            print(msg.hex())
            continue
        if mode == "decrypt":
            pt = tfsc.decrypt(msg, key)
            print(pt)
            continue
        else:
            return None
while True:
    machine = input("Nhập hệ thống bạn muốn dùng: ")
    if machine == "atbash":
        atbash_mc()
        continue
    if machine == "caesar":
        caesar_mc()
        continue
    if machine == "enigma":
        enigma_mc()
        continue
    if machine == "vigenere":
        vigenere_mc()
        continue
    if machine == "tbc":
        tbc_mc()
        continue
    if machine == "tfsc":
        tfsc_mc()
        continue
    break