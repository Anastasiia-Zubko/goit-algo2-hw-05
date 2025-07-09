import hashlib
from typing import Iterable, Dict


class BloomFilter:

    def __init__(self, size: int, num_hashes: int):
        if size <= 0 or num_hashes <= 0:
            raise ValueError("size та num_hashes мають бути додатними")
        self.size = size
        self.num_hashes = num_hashes
        self._bits = bytearray(size)

    def _hashes(self, item: str):
        data = item.encode("utf‑8")
        for i in range(self.num_hashes):
            digest = hashlib.sha256(data + i.to_bytes(2, "little")).digest()
            yield int.from_bytes(digest, "big") % self.size

    def add(self, item: str) -> None:
        for pos in self._hashes(item):
            self._bits[pos] = 1

    def __contains__(self, item: str) -> bool:
        return all(self._bits[pos] for pos in self._hashes(item))


# Функція перевірки унікальності паролів

def check_password_uniqueness(bloom: BloomFilter, passwords: Iterable[str]) -> Dict[str, str]:
    results: Dict[str, str] = {}
    for pwd in passwords:
        if not pwd:
            results[pwd] = "некоректний пароль"
            continue

        if pwd in bloom:
            results[pwd] = "вже використаний"
        else:
            results[pwd] = "унікальний"
            bloom.add(pwd)
    return results

if __name__ == "__main__":
    # Ініціалізація фільтра Блума
    bloom = BloomFilter(size=1000, num_hashes=3)

    # Додавання існуючих паролів
    existing_passwords = ["password123", "admin123", "qwerty123"]
    for password in existing_passwords:
        bloom.add(password)

    # Перевірка нових паролів
    new_passwords_to_check = ["password123", "newpassword", "admin123", "guest"]
    results = check_password_uniqueness(bloom, new_passwords_to_check)

    # Виведення результатів
    for password, status in results.items():
        print(f"Пароль '{password}' - {status}.")
