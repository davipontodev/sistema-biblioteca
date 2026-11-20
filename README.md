# Sistema de Biblioteca 📚

Sistema de gerenciamento de biblioteca feito em Python com banco de dados SQLite, usado pelo terminal. Controla livros, leitores, empréstimos, devoluções e atrasos.

Projeto feito para praticar **Banco de Dados** e **Algoritmos e Programação** do curso de TI da UFMS: modelagem de tabelas, chaves estrangeiras, `JOIN`, `GROUP BY` e integração do Python com SQL.

## Funcionalidades

- **Cadastro de livros** com título, autor, ano e quantidade de exemplares.
- **Busca de livros** por título ou autor, mostrando quantos exemplares estão disponíveis.
- **Cadastro de leitores** com e-mail único.
- **Empréstimos:** só permite emprestar se houver exemplar disponível. O prazo de devolução é de 14 dias.
- **Devoluções:** calcula automaticamente os dias de atraso.
- **Relatórios:** empréstimos em aberto, empréstimos atrasados e ranking dos livros mais emprestados.
- **Dados de exemplo** para testar o sistema rapidamente (opção 10 do menu).
- **Consultas SQL prontas** no arquivo `consultas.sql`.

## Tecnologias Utilizadas

- Python 3 (somente bibliotecas padrão)
- SQLite3

## Modelo do Banco de Dados

```
livros                   emprestimos                 leitores
-----------              -----------------           ----------
id (PK)        1 ──── N  id (PK)          N ──── 1   id (PK)
titulo                   livro_id (FK)               nome
autor                    leitor_id (FK)              email (único)
ano                      data_emprestimo
quantidade               data_prevista
                         data_devolucao
```

A quantidade de exemplares disponíveis não é guardada no banco: ela é calculada com `quantidade - empréstimos em aberto`, o que evita dados inconsistentes.

## Como Executar o Projeto

1. Clone ou baixe este repositório:
   ```bash
   git clone https://github.com/davipontodev/sistema-biblioteca.git
   ```
2. Entre na pasta e execute:
   ```bash
   cd sistema-biblioteca
   python biblioteca.py
   ```
3. Escolha a opção **10** para carregar os dados de exemplo e explore o menu.

O arquivo `biblioteca.db` é criado automaticamente na primeira execução.

## Exemplo de uso

```
  ID  Título                          Autor                 Ano    Disp.
  ----------------------------------------------------------------------
  1   Dom Casmurro                    Machado de Assis      1899    0/2
  3   Lógica de Programação           André Forbellone      2005    2/3
  2   O Cortiço                       Aluísio Azevedo       1890    1/1
  5   Sistemas de Banco de Dados      Elmasri e Navathe     2011    1/1
  4   Use a Cabeça! Python            Paul Barry            2018    2/2
```
