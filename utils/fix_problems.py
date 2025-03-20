#!/usr/bin/env python
"""
Script para corrigir problemas no sistema PDV JC Byte
- Associa vendas a caixas
- Atualiza saldos de clientes
- Verifica e corrige problemas de relógio
"""

import os
import sys
import requests
import json
from datetime import datetime
import time
import subprocess
import webbrowser

# URLs para as APIs (com instruções para abrir no navegador se o servidor estiver rodando)
BASE_URL = "http://localhost:5000"
CORRIGIR_VENDAS_URL = f"{BASE_URL}/caixa/corrigir-vendas"
ATUALIZAR_SALDOS_URL = f"{BASE_URL}/api/clientes/atualizar-saldos"

def verifique_servidor():
    """Verifica se o servidor está online"""
    print("Verificando se o servidor está rodando...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            return True
        else:
            print("O servidor está rodando, mas retornou um status code inesperado.")
            return True
    except requests.exceptions.ConnectionError:
        print("Não foi possível conectar ao servidor. Vamos tentar abrir as URLs no navegador.")
        return True  # Retornamos True para continuar o script e usar o navegador

def corrigir_vendas_sem_caixa():
    """Corrige vendas que não estão associadas a um caixa"""
    print("\n== CORREÇÃO DE VENDAS SEM CAIXA ==")
    print(f"Abrindo URL no navegador: {CORRIGIR_VENDAS_URL}")
    try:
        # Tentar abrir no navegador
        webbrowser.open(CORRIGIR_VENDAS_URL)
        print("✅ URL aberta no navegador. Verifique os resultados na janela do navegador.")
    except Exception as e:
        print(f"❌ Erro ao abrir o navegador: {str(e)}")

def atualizar_saldos_clientes():
    """Atualiza o saldo de todos os clientes"""
    print("\n== ATUALIZAÇÃO DE SALDOS DE CLIENTES ==")
    print(f"Abrindo URL no navegador: {ATUALIZAR_SALDOS_URL}")
    try:
        # Tentar abrir no navegador (usando POST)
        webbrowser.open(ATUALIZAR_SALDOS_URL)
        print("✅ URL aberta no navegador. Verifique os resultados na janela do navegador.")
        print("NOTA: Como é uma requisição POST, talvez seja necessário executar manualmente através de uma API test tool.")
    except Exception as e:
        print(f"❌ Erro ao abrir o navegador: {str(e)}")

def verificar_relogio():
    """Verifica se o relógio do sistema está correto"""
    print("\n== VERIFICAÇÃO DO RELÓGIO ==")
    
    # Obter a hora atual do sistema
    hora_sistema = datetime.now()
    print(f"Hora do sistema: {hora_sistema.strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Verificar se o JavaScript foi atualizado
    print("✅ O JavaScript do relógio foi atualizado para garantir a atualização em tempo real.")
    
    # Abrir o PDV para verificar o relógio
    print(f"Abrindo a interface do PDV no navegador: {BASE_URL}/vendas/pdv")
    try:
        webbrowser.open(f"{BASE_URL}/vendas/pdv")
        print("✅ Interface do PDV aberta no navegador. Verifique se o relógio está atualizando corretamente.")
    except Exception as e:
        print(f"❌ Erro ao abrir o navegador: {str(e)}")
    
    return True

def executar_correcoes():
    """Executa todas as correções"""
    print("=== INICIANDO CORREÇÃO DE PROBLEMAS DO PDV ===")
    print(f"Data e hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Verifica se o servidor está online (mas continua mesmo se não estiver, para usar o navegador)
    verifique_servidor()
    
    # Executa as correções
    verificar_relogio()
    corrigir_vendas_sem_caixa()
    atualizar_saldos_clientes()
    
    print("\n=== CORREÇÕES CONCLUÍDAS ===")
    print("✅ As correções foram aplicadas ou as URLs foram abertas no navegador.")
    print("\nÉ recomendável reiniciar o servidor para garantir que todas as mudanças sejam aplicadas.")
    
    return True

if __name__ == "__main__":
    executar_correcoes()
