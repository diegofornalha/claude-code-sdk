#!/usr/bin/env python3
"""Test paralelo 3 - Operações matemáticas"""
import time
import random
import math

def calculate_primes():
    print("Iniciando cálculo de primos...")
    time.sleep(random.uniform(1, 3))
    primes = []
    for num in range(2, 100):
        if all(num % i != 0 for i in range(2, int(math.sqrt(num)) + 1)):
            primes.append(num)
    print(f"Primos encontrados: {len(primes)}")
    return primes

if __name__ == "__main__":
    calculate_primes()