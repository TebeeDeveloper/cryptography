from tbcryptography import atbash, caesar, EnigmaMachine, vigenere, tbc, tfsc
from base64 import b85encode, b85decode

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
        msg = input("Nhập tin nhắn của bạn:\n>>>>")
        if msg == "quit()":
            return None
        key = eval(input("Nhập khóa của bạn: "))
        if mode == "encrypt":
            print(tfsc.process(msg, key).hex())
        else:
            print(tfsc.process(msg, key).decode())
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