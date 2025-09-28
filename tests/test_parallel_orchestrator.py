#!/usr/bin/env python3
"""Orquestrador de testes paralelos"""
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

def run_test(script_name):
    """Executa um script de teste e retorna o resultado"""
    start_time = time.time()
    try:
        result = subprocess.run(
            ['python3', f'tests/{script_name}'],
            capture_output=True,
            text=True,
            timeout=10
        )
        elapsed = time.time() - start_time
        return {
            'script': script_name,
            'success': result.returncode == 0,
            'elapsed_time': elapsed,
            'output': result.stdout,
            'error': result.stderr
        }
    except subprocess.TimeoutExpired:
        return {
            'script': script_name,
            'success': False,
            'elapsed_time': 10,
            'output': '',
            'error': 'Timeout após 10 segundos'
        }

def main():
    scripts = ['test_parallel_1.py', 'test_parallel_2.py', 'test_parallel_3.py']

    print("🚀 Iniciando execução paralela de testes...")
    print(f"📋 Scripts a executar: {scripts}")
    print("-" * 50)

    start_total = time.time()
    results = []

    # Execução paralela usando ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(run_test, script): script for script in scripts}

        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['script']} - {result['elapsed_time']:.2f}s")
            if result['output']:
                print(f"   Output: {result['output'].strip()}")
            if result['error']:
                print(f"   Error: {result['error'].strip()}")

    total_time = time.time() - start_total
    print("-" * 50)
    print(f"⏱️  Tempo total de execução: {total_time:.2f}s")
    print(f"📊 Taxa de sucesso: {sum(r['success'] for r in results)}/{len(results)}")

    # Salvar resultados
    with open('tests/parallel_results.json', 'w') as f:
        json.dump({
            'total_time': total_time,
            'results': results
        }, f, indent=2)

    print("💾 Resultados salvos em tests/parallel_results.json")

if __name__ == "__main__":
    main()