import os
import sys
import sqlite3
from datetime import datetime

print("Script de migração para adicionar o campo 'description' à tabela 'sales'")
print("================================================================")

# Caminho do banco de dados
db_path = 'instance/pdv.db'

if not os.path.exists(db_path):
    print(f"ERRO: Banco de dados '{db_path}' não encontrado!")
    sys.exit(1)

try:
    # Conecta ao banco de dados
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Verifica se a coluna já existe
    cursor.execute("PRAGMA table_info(sales)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    
    if 'description' in column_names:
        print("A coluna 'description' já existe na tabela 'sales'. Nenhuma ação necessária.")
    else:
        # Adiciona a coluna description
        cursor.execute("ALTER TABLE sales ADD COLUMN description TEXT;")
        conn.commit()
        print("Coluna 'description' adicionada com sucesso à tabela 'sales'!")
    
    print("\nMigração concluída com sucesso!")
    
except sqlite3.Error as e:
    print(f"ERRO SQLite: {e}")
    sys.exit(1)
except Exception as e:
    print(f"ERRO: {e}")
    sys.exit(1)
finally:
    if conn:
        conn.close()
