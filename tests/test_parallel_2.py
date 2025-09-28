#!/usr/bin/env python3
"""Test paralelo 2 - Análise de strings"""
import time
import random

def analyze_text():
    print("Iniciando análise paralelo 2...")
    time.sleep(random.uniform(1, 3))
    text = "Claude Code SDK Test Paralelo" * 100
    result = len(text.split())
    print(f"Palavras analisadas: {result}")
    return result

if __name__ == "__main__":
    analyze_text()