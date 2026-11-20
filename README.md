# sistema-biblioteca

Projeto que fiz para praticar Python com banco de dados (SQLite), junto com a disciplina de Banco de Dados da faculdade (TI - UFMS).

É um sistema de biblioteca simples que roda no terminal. Dá pra cadastrar livros e leitores, fazer empréstimos e devoluções, e ver quem está com livro atrasado.

## O que ele faz

- cadastra livros (título, autor, ano e quantidade de exemplares)
- busca livro por título ou autor
- cadastra leitores (o e-mail não pode repetir)
- registra empréstimo, mas só se tiver exemplar disponível
- registra devolução e mostra quantos dias atrasou (o prazo é 14 dias)
- lista empréstimos em aberto e atrasados
- mostra os livros mais emprestados
- tem uma opção pra colocar dados de exemplo e testar mais rápido

## Banco de dados

Usei 3 tabelas: `livros`, `leitores` e `emprestimos`. A tabela de empréstimos liga as outras duas pelas chaves estrangeiras (`livro_id` e `leitor_id`).

```
livros (1) ---- (N) emprestimos (N) ---- (1) leitores
```

Não guardei a quantidade disponível no banco. Ela é calculada na consulta (quantidade total menos os empréstimos que ainda não foram devolvidos), assim não corre o risco de ficar com número errado.

No arquivo `consultas.sql` deixei algumas consultas que usei pra estudar `JOIN`, `GROUP BY` e subconsulta.

## Como rodar

Precisa ter o Python 3 instalado. Não precisa instalar nenhuma biblioteca.

```bash
git clone https://github.com/davipontodev/sistema-biblioteca.git
cd sistema-biblioteca
python biblioteca.py
```

Na primeira vez ele cria o arquivo `biblioteca.db` sozinho. Escolha a opção 10 no menu pra carregar os dados de exemplo.

## Exemplo

```
  ID  Título                          Autor                 Ano    Disp.
  ----------------------------------------------------------------------
  1   Dom Casmurro                    Machado de Assis      1899    0/2
  3   Lógica de Programação           André Forbellone      2005    2/3
  2   O Cortiço                       Aluísio Azevedo       1890    1/1
  5   Sistemas de Banco de Dados      Elmasri e Navathe     2011    1/1
  4   Use a Cabeça! Python            Paul Barry            2018    2/2
```

## O que quero melhorar

- fazer uma interface gráfica ou versão web
- adicionar multa por atraso
- separar o código em mais arquivos
