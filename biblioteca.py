"""
Sistema de Biblioteca
Gerencia livros, leitores e empréstimos usando Python e SQLite pelo terminal.
"""

import sqlite3
from datetime import date, timedelta

BANCO = "biblioteca.db"
DIAS_EMPRESTIMO = 14


# ---------------------------------------------------------------------------
# Banco de dados
# ---------------------------------------------------------------------------

def conectar():
    con = sqlite3.connect(BANCO)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def criar_tabelas(con):
    con.executescript("""
        CREATE TABLE IF NOT EXISTS livros (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo      TEXT NOT NULL,
            autor       TEXT NOT NULL,
            ano         INTEGER,
            quantidade  INTEGER NOT NULL DEFAULT 1 CHECK (quantidade >= 0)
        );

        CREATE TABLE IF NOT EXISTS leitores (
            id     INTEGER PRIMARY KEY AUTOINCREMENT,
            nome   TEXT NOT NULL,
            email  TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS emprestimos (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            livro_id         INTEGER NOT NULL REFERENCES livros(id),
            leitor_id        INTEGER NOT NULL REFERENCES leitores(id),
            data_emprestimo  TEXT NOT NULL,
            data_prevista    TEXT NOT NULL,
            data_devolucao   TEXT
        );
    """)


# ---------------------------------------------------------------------------
# Regras do sistema
# ---------------------------------------------------------------------------

def cadastrar_livro(con, titulo, autor, ano, quantidade):
    cur = con.execute(
        "INSERT INTO livros (titulo, autor, ano, quantidade) VALUES (?, ?, ?, ?)",
        (titulo, autor, ano, quantidade),
    )
    con.commit()
    return cur.lastrowid


def cadastrar_leitor(con, nome, email):
    try:
        cur = con.execute("INSERT INTO leitores (nome, email) VALUES (?, ?)", (nome, email))
        con.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        raise ValueError("Já existe um leitor com esse e-mail.")


def listar_livros(con, busca=""):
    # A disponibilidade é calculada: quantidade total menos empréstimos em aberto
    termo = f"%{busca}%"
    return con.execute("""
        SELECT l.id, l.titulo, l.autor, l.ano, l.quantidade,
               l.quantidade - COUNT(e.id) AS disponiveis
        FROM livros l
        LEFT JOIN emprestimos e
               ON e.livro_id = l.id AND e.data_devolucao IS NULL
        WHERE l.titulo LIKE ? OR l.autor LIKE ?
        GROUP BY l.id
        ORDER BY l.titulo
    """, (termo, termo)).fetchall()


def listar_leitores(con):
    return con.execute("SELECT id, nome, email FROM leitores ORDER BY nome").fetchall()


def emprestar(con, livro_id, leitor_id, hoje=None):
    hoje = hoje or date.today()

    livro = con.execute("""
        SELECT l.titulo, l.quantidade - COUNT(e.id) AS disponiveis
        FROM livros l
        LEFT JOIN emprestimos e ON e.livro_id = l.id AND e.data_devolucao IS NULL
        WHERE l.id = ?
        GROUP BY l.id
    """, (livro_id,)).fetchone()
    if not livro:
        raise ValueError("Livro não encontrado.")
    if livro["disponiveis"] <= 0:
        raise ValueError(f"Não há exemplares disponíveis de \"{livro['titulo']}\".")

    if not con.execute("SELECT 1 FROM leitores WHERE id = ?", (leitor_id,)).fetchone():
        raise ValueError("Leitor não encontrado.")

    prevista = hoje + timedelta(days=DIAS_EMPRESTIMO)
    cur = con.execute(
        "INSERT INTO emprestimos (livro_id, leitor_id, data_emprestimo, data_prevista) "
        "VALUES (?, ?, ?, ?)",
        (livro_id, leitor_id, hoje.isoformat(), prevista.isoformat()),
    )
    con.commit()
    return cur.lastrowid, prevista


def devolver(con, emprestimo_id, hoje=None):
    hoje = hoje or date.today()
    emp = con.execute(
        "SELECT data_prevista, data_devolucao FROM emprestimos WHERE id = ?", (emprestimo_id,)
    ).fetchone()
    if not emp:
        raise ValueError("Empréstimo não encontrado.")
    if emp["data_devolucao"]:
        raise ValueError("Esse empréstimo já foi devolvido.")

    con.execute(
        "UPDATE emprestimos SET data_devolucao = ? WHERE id = ?", (hoje.isoformat(), emprestimo_id)
    )
    con.commit()
    dias_atraso = (hoje - date.fromisoformat(emp["data_prevista"])).days
    return max(dias_atraso, 0)


def emprestimos_em_aberto(con):
    return con.execute("""
        SELECT e.id, l.titulo, r.nome AS leitor, e.data_emprestimo, e.data_prevista
        FROM emprestimos e
        JOIN livros l   ON l.id = e.livro_id
        JOIN leitores r ON r.id = e.leitor_id
        WHERE e.data_devolucao IS NULL
        ORDER BY e.data_prevista
    """).fetchall()


def emprestimos_atrasados(con, hoje=None):
    hoje = hoje or date.today()
    return [e for e in emprestimos_em_aberto(con) if e["data_prevista"] < hoje.isoformat()]


def livros_mais_emprestados(con, limite=5):
    return con.execute("""
        SELECT l.titulo, l.autor, COUNT(e.id) AS total
        FROM livros l
        JOIN emprestimos e ON e.livro_id = l.id
        GROUP BY l.id
        ORDER BY total DESC, l.titulo
        LIMIT ?
    """, (limite,)).fetchall()


def inserir_dados_exemplo(con):
    if con.execute("SELECT COUNT(*) FROM livros").fetchone()[0] > 0:
        return False

    livros = [
        ("Dom Casmurro", "Machado de Assis", 1899, 2),
        ("O Cortiço", "Aluísio Azevedo", 1890, 1),
        ("Lógica de Programação", "André Forbellone", 2005, 3),
        ("Use a Cabeça! Python", "Paul Barry", 2018, 2),
        ("Sistemas de Banco de Dados", "Elmasri e Navathe", 2011, 1),
    ]
    for livro in livros:
        cadastrar_livro(con, *livro)

    cadastrar_leitor(con, "Ana Souza", "ana@email.com")
    cadastrar_leitor(con, "Bruno Lima", "bruno@email.com")
    return True


# ---------------------------------------------------------------------------
# Interface no terminal
# ---------------------------------------------------------------------------

def ler_texto(mensagem):
    while True:
        valor = input(mensagem).strip()
        if valor:
            return valor
        print("  Campo obrigatório.")


def ler_inteiro(mensagem, minimo=None, opcional=False):
    while True:
        valor = input(mensagem).strip()
        if opcional and valor == "":
            return None
        try:
            numero = int(valor)
            if minimo is not None and numero < minimo:
                print(f"  Digite um número maior ou igual a {minimo}.")
                continue
            return numero
        except ValueError:
            print("  Digite um número inteiro.")


def data_br(iso):
    return date.fromisoformat(iso).strftime("%d/%m/%Y")


def mostrar_livros(livros):
    if not livros:
        print("  Nenhum livro encontrado.")
        return
    print(f"\n  {'ID':<4}{'Título':<32}{'Autor':<22}{'Ano':<6}{'Disp.':>6}")
    print("  " + "-" * 70)
    for l in livros:
        ano = l["ano"] if l["ano"] else "-"
        print(f"  {l['id']:<4}{l['titulo'][:30]:<32}{l['autor'][:20]:<22}{ano!s:<6}"
              f"{l['disponiveis']:>3}/{l['quantidade']}")


def mostrar_emprestimos(emprestimos):
    if not emprestimos:
        print("  Nenhum empréstimo.")
        return
    print(f"\n  {'ID':<4}{'Livro':<32}{'Leitor':<20}{'Devolver até':>12}")
    print("  " + "-" * 68)
    for e in emprestimos:
        print(f"  {e['id']:<4}{e['titulo'][:30]:<32}{e['leitor'][:18]:<20}{data_br(e['data_prevista']):>12}")


MENU = """
========== SISTEMA DE BIBLIOTECA ==========
 1. Cadastrar livro
 2. Listar / buscar livros
 3. Cadastrar leitor
 4. Listar leitores
 5. Registrar empréstimo
 6. Registrar devolução
 7. Empréstimos em aberto
 8. Empréstimos atrasados
 9. Livros mais emprestados
10. Inserir dados de exemplo
 0. Sair
==========================================="""


def main():
    con = conectar()
    criar_tabelas(con)

    while True:
        print(MENU)
        opcao = input("Escolha uma opção: ").strip()

        try:
            if opcao == "1":
                titulo = ler_texto("Título: ")
                autor = ler_texto("Autor: ")
                ano = ler_inteiro("Ano (opcional): ", minimo=0, opcional=True)
                qtd = ler_inteiro("Quantidade de exemplares: ", minimo=1)
                novo_id = cadastrar_livro(con, titulo, autor, ano, qtd)
                print(f"  Livro cadastrado com ID {novo_id}.")

            elif opcao == "2":
                busca = input("Buscar por título ou autor (Enter para todos): ").strip()
                mostrar_livros(listar_livros(con, busca))

            elif opcao == "3":
                nome = ler_texto("Nome: ")
                email = ler_texto("E-mail: ")
                novo_id = cadastrar_leitor(con, nome, email)
                print(f"  Leitor cadastrado com ID {novo_id}.")

            elif opcao == "4":
                leitores = listar_leitores(con)
                if not leitores:
                    print("  Nenhum leitor cadastrado.")
                for r in leitores:
                    print(f"  {r['id']:<4}{r['nome']:<25}{r['email']}")

            elif opcao == "5":
                mostrar_livros(listar_livros(con))
                livro_id = ler_inteiro("\nID do livro: ")
                leitor_id = ler_inteiro("ID do leitor: ")
                emp_id, prevista = emprestar(con, livro_id, leitor_id)
                print(f"  Empréstimo {emp_id} registrado. Devolver até {prevista.strftime('%d/%m/%Y')}.")

            elif opcao == "6":
                mostrar_emprestimos(emprestimos_em_aberto(con))
                emp_id = ler_inteiro("\nID do empréstimo: ")
                atraso = devolver(con, emp_id)
                if atraso:
                    print(f"  Devolução registrada com {atraso} dia(s) de atraso.")
                else:
                    print("  Devolução registrada no prazo.")

            elif opcao == "7":
                mostrar_emprestimos(emprestimos_em_aberto(con))

            elif opcao == "8":
                mostrar_emprestimos(emprestimos_atrasados(con))

            elif opcao == "9":
                ranking = livros_mais_emprestados(con)
                if not ranking:
                    print("  Ainda não há empréstimos.")
                for posicao, l in enumerate(ranking, start=1):
                    print(f"  {posicao}º {l['titulo']} ({l['autor']}) - {l['total']} empréstimo(s)")

            elif opcao == "10":
                if inserir_dados_exemplo(con):
                    print("  Dados de exemplo inseridos.")
                else:
                    print("  O banco já tem livros cadastrados.")

            elif opcao == "0":
                print("Até logo!")
                break

            else:
                print("  Opção inválida.")

        except ValueError as e:
            print(f"  Erro: {e}")

    con.close()


if __name__ == "__main__":
    main()
