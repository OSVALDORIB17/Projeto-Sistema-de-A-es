import sqlite3
import os # Importado para ajudar a gerenciar o arquivo do banco de dados

# Nome do arquivo do banco de dados
DB_FILE = 'portfolio_acoes.db'

# --- Funções de Banco de Dados ---

def conectar():
    """Conecta ao banco de dados ou cria o arquivo se não existir."""
    # Usamos 'with' para garantir que a conexão seja fechada automaticamente
    return sqlite3.connect(DB_FILE)

def criar_tabela():
    """Cria a tabela ACOES se ela ainda não existir."""
    conn = conectar()
    cursor = conn.cursor()
    # SQL para criar a tabela com os tipos de dados corretos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ACOES (
            ticker TEXT PRIMARY KEY,
            empresa TEXT NOT NULL,
            quantidade REAL NOT NULL,
            preco_medio REAL NOT NULL
        );
    ''')
    conn.commit() # Confirma a criação da tabela
    conn.close()

# --- Funções do Sistema (CRUD com SQLite) ---

def criar_acao_db(ticker, empresa, quantidade, preco):
    """Operação CREATE: Adiciona uma nova ação ao banco de dados."""
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO ACOES (ticker, empresa, quantidade, preco_medio) VALUES (?, ?, ?, ?)",
                       (ticker.upper(), empresa, quantidade, preco))
        conn.commit()
        print(f"\nSUCESSO: Ação {ticker.upper()} adicionada ao portfolio.")
    except sqlite3.IntegrityError:
        # Lida com a tentativa de inserir um ticker duplicado (chave primária)
        print(f"\nERRO: Ação {ticker.upper()} já existe. Use a função de Atualizar.")
    finally:
        conn.close()

def ler_portfolio_db():
    """Operação READ: Exibe todas as ações do banco de dados."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT ticker, empresa, quantidade, preco_medio FROM ACOES ORDER BY ticker")
    acoes = cursor.fetchall() # Obtém todos os resultados
    conn.close()

    print("\n--- PORTFOLIO DE AÇÕES (SQLite) ---")
    if not acoes:
        print("Seu portfolio está vazio.")
        return

    print(f"{'TICKER':<10} | {'EMPRESA':<20} | {'QTD':<5} | {'PREÇO MÉDIO':<12} | {'VALOR TOTAL':<12}")
    print("-" * 65)
    valor_total_portfolio = 0
    for acao in acoes:
        ticker, empresa, quantidade, preco_medio = acao
        valor_total_acao = quantidade * preco_medio
        valor_total_portfolio += valor_total_acao
        print(f"{ticker:<10} | {empresa:<20} | {quantidade:<5.1f} | R${preco_medio:<10.2f} | R${valor_total_acao:<10.2f}")
    print("-" * 65)
    print(f"VALOR TOTAL DO PORTFOLIO: R${valor_total_portfolio:.2f}")

def atualizar_acao_db(ticker, nova_quantidade, novo_preco):
    """Operação UPDATE: Atualiza a quantidade e o preço médio de uma ação existente no banco de dados."""
    conn = conectar()
    cursor = conn.cursor()
    
    # Primeiro, recuperamos os dados atuais para recalcular o preço médio ponderado
    cursor.execute("SELECT quantidade, preco_medio FROM ACOES WHERE ticker = ?", (ticker.upper(),))
    dados_atuais = cursor.fetchone()

    if dados_atuais:
        qtd_antiga, preco_antigo = dados_atuais
        qtd_total = qtd_antiga + nova_quantidade
        
        # Evita divisão por zero se a quantidade total for zero
        if qtd_total == 0:
            novo_preco_medio = 0.0
        else:
            valor_total_antigo = qtd_antiga * preco_antigo
            valor_novo_investimento = nova_quantidade * novo_preco
            novo_preco_medio = (valor_total_antigo + valor_novo_investimento) / qtd_total

        # Executa o UPDATE no banco de dados
        cursor.execute("UPDATE ACOES SET quantidade = ?, preco_medio = ? WHERE ticker = ?", 
                       (qtd_total, novo_preco_medio, ticker.upper()))
        conn.commit()
        print(f"\nSUCESSO: Ação {ticker.upper()} atualizada. Nova QTD: {qtd_total:.1f}")
    else:
        print(f"\nERRO: Ação {ticker.upper()} não encontrada no portfolio.")
        
    conn.close()

def deletar_acao_db(ticker):
    """Operação DELETE: Remove uma ação do banco de dados."""
    conn = conectar()
    cursor = conn.cursor()
    # Executa o DELETE no banco de dados
    cursor.execute("DELETE FROM ACOES WHERE ticker = ?", (ticker.upper(),))
    conn.commit()

    if cursor.rowcount > 0:
        print(f"\nSUCESSO: Ação {ticker.upper()} removida do portfolio.")
    else:
        print(f"\nERRO: Ação {ticker.upper()} não encontrada no portfolio.")

    conn.close()

def menu_principal():
    """Função principal que gerencia a interação com o usuário."""
    # Garante que a tabela exista antes de iniciar o menu
    criar_tabela() 
    
    while True:
        print("\n===============================")
        print(f"  SISTEMA DE AÇÕES (DB: {DB_FILE})")
        print("===============================")
        print("1. Adicionar nova ação (CREATE)")
        print("2. Visualizar portfolio (READ)")
        print("3. Atualizar/Adicionar mais ações (UPDATE)")
        print("4. Remover ação (DELETE)")
        print("5. Sair")
        
        escolha = input("Escolha uma opção: ")

        if escolha == '1':
            ticker = input("Ticker da ação (ex: PETR4): ")
            empresa = input("Nome da empresa: ")
            quantidade = float(input("Quantidade comprada: "))
            preco = float(input("Preço médio por ação: "))
            criar_acao_db(ticker, empresa, quantidade, preco)
        elif escolha == '2':
            ler_portfolio_db()
        elif escolha == '3':
            ticker = input("Ticker da ação para atualizar (ex: PETR4): ")
            quantidade = float(input("Quantidade adicional comprada (positiva para compra): "))
            preco = float(input("Preço pago nesta operação: "))
            atualizar_acao_db(ticker, quantidade, preco)
        elif escolha == '4':
            ticker = input("Ticker da ação a ser removida: ")
            deletar_acao_db(ticker)
        elif escolha == '5':
            print("Saindo do sistema. Até mais!")
            break
        else:
            print("\nOpção inválida. Tente novamente.")

# --- Execução do Programa ---
if __name__ == "__main__":
    menu_principal()
