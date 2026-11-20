"""
Versão web do sistema de biblioteca, feita com Flask.
Usa as mesmas funções do biblioteca.py (a versão de terminal continua funcionando).
"""

import os
from contextlib import closing
from datetime import date

from flask import Flask, flash, redirect, render_template, request, url_for

import biblioteca as bib

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "chave_biblioteca_dev")


def abrir_banco():
    con = bib.conectar()
    bib.criar_tabelas(con)
    return con


# Coloca os dados de exemplo pra quem abrir o site já ver alguma coisa
with closing(abrir_banco()) as con:
    bib.inserir_dados_exemplo(con)


def ler_inteiro(nome_campo):
    try:
        return int(request.form.get(nome_campo, ""))
    except ValueError:
        return None


@app.route("/")
def livros():
    busca = request.args.get("busca", "").strip()
    with closing(abrir_banco()) as con:
        lista = bib.listar_livros(con, busca)
    return render_template("pagina.html", aba="livros", livros=lista, busca=busca)


@app.route("/livros", methods=["POST"])
def cadastrar_livro():
    titulo = request.form.get("titulo", "").strip()
    autor = request.form.get("autor", "").strip()
    ano = ler_inteiro("ano")
    quantidade = ler_inteiro("quantidade")

    if not titulo or not autor or not quantidade or quantidade < 1:
        flash("Preencha título, autor e uma quantidade maior que zero.", "erro")
        return redirect(url_for("livros"))

    with closing(abrir_banco()) as con:
        bib.cadastrar_livro(con, titulo, autor, ano, quantidade)
    flash(f'Livro "{titulo}" cadastrado!', "ok")
    return redirect(url_for("livros"))


@app.route("/leitores", methods=["GET", "POST"])
def leitores():
    with closing(abrir_banco()) as con:
        if request.method == "POST":
            nome = request.form.get("nome", "").strip()
            email = request.form.get("email", "").strip()
            if not nome or not email:
                flash("Preencha nome e e-mail.", "erro")
            else:
                try:
                    bib.cadastrar_leitor(con, nome, email)
                    flash(f"Leitor {nome} cadastrado!", "ok")
                except ValueError as erro:
                    flash(str(erro), "erro")
            return redirect(url_for("leitores"))

        lista = bib.listar_leitores(con)
    return render_template("pagina.html", aba="leitores", leitores=lista)


@app.route("/emprestimos", methods=["GET", "POST"])
def emprestimos():
    with closing(abrir_banco()) as con:
        if request.method == "POST":
            livro_id = ler_inteiro("livro_id")
            leitor_id = ler_inteiro("leitor_id")
            try:
                _, prevista = bib.emprestar(con, livro_id, leitor_id)
                flash(f"Empréstimo registrado! Devolver até {prevista.strftime('%d/%m/%Y')}.", "ok")
            except ValueError as erro:
                flash(str(erro), "erro")
            return redirect(url_for("emprestimos"))

        abertos = bib.emprestimos_em_aberto(con)
        livros_disponiveis = [l for l in bib.listar_livros(con) if l["disponiveis"] > 0]
        lista_leitores = bib.listar_leitores(con)

    return render_template(
        "pagina.html",
        aba="emprestimos",
        emprestimos=abertos,
        livros=livros_disponiveis,
        leitores=lista_leitores,
        hoje=date.today().isoformat(),
    )


@app.route("/devolver/<int:emprestimo_id>", methods=["POST"])
def devolver(emprestimo_id):
    with closing(abrir_banco()) as con:
        try:
            atraso = bib.devolver(con, emprestimo_id)
            if atraso:
                flash(f"Devolução registrada com {atraso} dia(s) de atraso.", "erro")
            else:
                flash("Devolução registrada no prazo.", "ok")
        except ValueError as erro:
            flash(str(erro), "erro")
    return redirect(url_for("emprestimos"))


@app.route("/relatorios")
def relatorios():
    with closing(abrir_banco()) as con:
        ranking = bib.livros_mais_emprestados(con)
        atrasados = bib.emprestimos_atrasados(con)
    return render_template("pagina.html", aba="relatorios", ranking=ranking, atrasados=atrasados)


@app.template_filter("data_br")
def filtro_data_br(iso):
    return bib.data_br(iso)


if __name__ == "__main__":
    app.run(debug=True)
