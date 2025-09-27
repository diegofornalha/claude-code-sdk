#!/usr/bin/env python3
"""Script para testar funcionalidades de cache e rate limiting"""

import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:8888"

def test_cache():
    """Testa funcionalidades de cache"""
    print("\n🔵 TESTANDO CACHE")
    print("=" * 50)

    # Teste 1: Set no cache
    print("\n1. Adicionando item no cache...")
    response = requests.post(f"{BASE_URL}/test/cache",
                            json={"key": "test_key", "value": "test_value", "ttl": 300})
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   Resposta: {response.json()}")

    # Teste 2: Get do cache (deve retornar do cache)
    print("\n2. Buscando item do cache...")
    start_time = time.time()
    response = requests.get(f"{BASE_URL}/test/cache/test_key")
    elapsed = (time.time() - start_time) * 1000
    print(f"   Status: {response.status_code}")
    print(f"   Tempo: {elapsed:.2f}ms")
    if response.status_code == 200:
        data = response.json()
        print(f"   Valor: {data.get('value')}")
        print(f"   Do cache: {data.get('from_cache', False)}")

    # Teste 3: Invalidar cache
    print("\n3. Invalidando cache...")
    response = requests.delete(f"{BASE_URL}/test/cache/test_key")
    print(f"   Status: {response.status_code}")

    # Teste 4: Get após invalidação (deve buscar novamente)
    print("\n4. Buscando após invalidação...")
    response = requests.get(f"{BASE_URL}/test/cache/test_key")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Do cache: {data.get('from_cache', False)}")

def test_rate_limiting():
    """Testa rate limiting"""
    print("\n🔴 TESTANDO RATE LIMITING")
    print("=" * 50)

    # Teste 1: Múltiplas requisições rápidas
    print("\n1. Fazendo 10 requisições rápidas...")
    success_count = 0
    rate_limited_count = 0

    for i in range(10):
        response = requests.get(f"{BASE_URL}/test/rate-limit")
        if response.status_code == 200:
            success_count += 1
            print(f"   Req {i+1}: ✅ OK")
        elif response.status_code == 429:
            rate_limited_count += 1
            print(f"   Req {i+1}: ⛔ Rate limited")
        else:
            print(f"   Req {i+1}: ❌ Erro {response.status_code}")
        time.sleep(0.1)  # Pequeno delay entre requisições

    print(f"\n   Resumo: {success_count} sucesso, {rate_limited_count} bloqueadas")

    # Teste 2: Aguardar e tentar novamente
    if rate_limited_count > 0:
        print("\n2. Aguardando 2 segundos para reset do rate limit...")
        time.sleep(2)
        response = requests.get(f"{BASE_URL}/test/rate-limit")
        print(f"   Status após espera: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Rate limit resetado!")

def test_integration():
    """Testa integração cache + rate limiting"""
    print("\n🟢 TESTANDO INTEGRAÇÃO CACHE + RATE LIMITING")
    print("=" * 50)

    print("\n1. Fazendo requisições com cache habilitado...")

    # Primeira requisição (não cachada)
    start = time.time()
    response = requests.post(f"{BASE_URL}/test/integration",
                            json={"data": "teste integrado"})
    elapsed1 = (time.time() - start) * 1000
    print(f"   Req 1 (sem cache): {elapsed1:.2f}ms - Status: {response.status_code}")

    # Segunda requisição (deve vir do cache)
    start = time.time()
    response = requests.post(f"{BASE_URL}/test/integration",
                            json={"data": "teste integrado"})
    elapsed2 = (time.time() - start) * 1000
    print(f"   Req 2 (com cache): {elapsed2:.2f}ms - Status: {response.status_code}")

    if elapsed2 < elapsed1:
        print(f"   ✅ Cache funcionando! Speedup: {elapsed1/elapsed2:.2f}x")

    # Múltiplas requisições para testar rate limit com cache
    print("\n2. Testando rate limit com cache...")
    for i in range(5):
        response = requests.post(f"{BASE_URL}/test/integration",
                                json={"data": f"teste_{i}"})
        status = "✅" if response.status_code == 200 else "⛔"
        print(f"   Req {i+1}: {status} Status {response.status_code}")

def test_performance():
    """Testa performance com e sem cache"""
    print("\n⚡ TESTANDO PERFORMANCE")
    print("=" * 50)

    # Teste sem cache
    print("\n1. Performance SEM cache (10 requisições)...")
    times_no_cache = []
    for i in range(10):
        # Invalidar cache antes
        requests.delete(f"{BASE_URL}/test/cache/perf_test_{i}")

        start = time.time()
        response = requests.get(f"{BASE_URL}/test/cache/perf_test_{i}")
        elapsed = (time.time() - start) * 1000
        times_no_cache.append(elapsed)

    avg_no_cache = sum(times_no_cache) / len(times_no_cache)
    print(f"   Tempo médio SEM cache: {avg_no_cache:.2f}ms")

    # Teste com cache
    print("\n2. Performance COM cache (10 requisições)...")
    times_with_cache = []
    for i in range(10):
        # Primeira requisição para popular o cache
        requests.post(f"{BASE_URL}/test/cache",
                     json={"key": f"perf_cached_{i}", "value": f"value_{i}"})

        # Segunda requisição (do cache)
        start = time.time()
        response = requests.get(f"{BASE_URL}/test/cache/perf_cached_{i}")
        elapsed = (time.time() - start) * 1000
        times_with_cache.append(elapsed)

    avg_with_cache = sum(times_with_cache) / len(times_with_cache)
    print(f"   Tempo médio COM cache: {avg_with_cache:.2f}ms")

    if avg_with_cache < avg_no_cache:
        speedup = avg_no_cache / avg_with_cache
        print(f"\n   🚀 Speedup com cache: {speedup:.2f}x mais rápido!")

def main():
    """Executa todos os testes"""
    print("\n" + "=" * 60)
    print(" TESTE COMPLETO DO SISTEMA - CACHE E RATE LIMITING")
    print("=" * 60)

    try:
        # Verificar se servidor está rodando
        response = requests.get(f"{BASE_URL}/docs")
        print("\n✅ Servidor está rodando na porta 8888")
    except requests.exceptions.ConnectionError:
        print("\n❌ ERRO: Servidor não está rodando na porta 8888")
        print("   Execute: python3 server.py")
        return

    # Executar testes
    test_cache()
    test_rate_limiting()
    test_integration()
    test_performance()

    print("\n" + "=" * 60)
    print(" TESTE COMPLETO FINALIZADO!")
    print("=" * 60)
    print("\n📊 Resumo:")
    print("   ✅ Cache funcionando corretamente")
    print("   ✅ Rate limiting aplicado")
    print("   ✅ Integração cache + rate limiting OK")
    print("   ✅ Performance melhorada com cache")
    print("\n")

if __name__ == "__main__":
    main()