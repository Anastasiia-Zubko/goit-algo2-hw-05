from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path
from typing import Iterable, List
import mmh3


LOGFILE = Path("/Users/anastasiiazubko/PycharmProjects/goit-algo2-hw-05/lms-stage-access.log")
PRECISION = 14


class HyperLogLog:
    def __init__(self, p: int = PRECISION):
        self.p = p
        self.m = 1 << p
        self.registers: List[int] = [0] * self.m
        self.alpha = self._get_alpha()
        self.small_range_correction = 5 * self.m / 2

    def _get_alpha(self) -> float:
        if self.p == 4:
            return 0.673
        elif self.p == 5:
            return 0.697
        elif self.p == 6:
            return 0.709
        return 0.7213 / (1 + 1.079 / self.m)

    def _hash64(self, value: str) -> int:
        return mmh3.hash64(value, signed=False)[0]

    def _rho(self, w: int) -> int:
        return (64 - w.bit_length()) + 1 if w else 64

    def add(self, item: str) -> None:
        x = self._hash64(str(item))
        j = x & (self.m - 1)
        w = x >> self.p
        self.registers[j] = max(self.registers[j], self._rho(w))

    def count(self) -> float:
        Z = sum(2.0 ** -r for r in self.registers)
        E = self.alpha * self.m * self.m / Z
        if E <= self.small_range_correction:
            V = self.registers.count(0)
            if V:
                E = self.m * math.log(self.m / V)
        return E

# Завантаження IP‑адрес з lms-stage-access.log

def load_ips(path: Path) -> Iterable[str]:
    with path.open(encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            try:
                obj = json.loads(line)
                ip = obj.get("remote_addr")
                if ip:
                    yield ip
            except json.JSONDecodeError:
                continue


def main() -> None:
    if not LOGFILE.exists():
        sys.exit(f"Log file not found → {LOGFILE}")

    ips = list(load_ips(LOGFILE))

    # ------ Точний підрахунок ------
    t0 = time.perf_counter()
    exact = len(set(ips))
    t_exact = time.perf_counter() - t0

    # ------ HyperLogLog ------
    t0 = time.perf_counter()
    hll = HyperLogLog(PRECISION)
    for ip in ips:
        hll.add(ip)
    approx = hll.count()
    t_hll = time.perf_counter() - t0

    print("\nРезультати порівняння:\n")
    print(f"{'':25}Точний підрахунок   HyperLogLog")
    print(f"Унікальні елементи{exact:18d}{approx:14.0f}")
    print(f"Час виконання (сек.){t_exact:14.4f}{t_hll:14.4f}\n")


if __name__ == "__main__":
    main()
