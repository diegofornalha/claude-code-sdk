#!/usr/bin/env python3
"""Test paralelo 1 - Processamento de dados"""
import time
import random

def process_data():
    print("Iniciando processamento paralelo 1...")
    time.sleep(random.uniform(1, 3))
    result = sum(range(1000000))
    print(f"Resultado paralelo 1: {result}")
    return result

if __name__ == "__main__":
    process_data()