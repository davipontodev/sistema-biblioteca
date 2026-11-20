-- Consultas úteis para estudar o banco biblioteca.db
-- Abra com: sqlite3 biblioteca.db  (ou no DB Browser for SQLite)

-- 1. Todos os livros com a quantidade de exemplares disponíveis
SELECT l.titulo,
       l.quantidade,
       l.quantidade - COUNT(e.id) AS disponiveis
FROM livros l
LEFT JOIN emprestimos e
       ON e.livro_id = l.id AND e.data_devolucao IS NULL
GROUP BY l.id
ORDER BY l.titulo;

-- 2. Empréstimos em aberto, com nome do livro e do leitor
SELECT e.id, l.titulo, r.nome, e.data_emprestimo, e.data_prevista
FROM emprestimos e
JOIN livros l   ON l.id = e.livro_id
JOIN leitores r ON r.id = e.leitor_id
WHERE e.data_devolucao IS NULL;

-- 3. Empréstimos atrasados (prazo menor que a data de hoje)
SELECT l.titulo, r.nome, e.data_prevista,
       CAST(julianday('now') - julianday(e.data_prevista) AS INTEGER) AS dias_atraso
FROM emprestimos e
JOIN livros l   ON l.id = e.livro_id
JOIN leitores r ON r.id = e.leitor_id
WHERE e.data_devolucao IS NULL
  AND e.data_prevista < date('now');

-- 4. Quantidade de empréstimos por leitor
SELECT r.nome, COUNT(e.id) AS total_emprestimos
FROM leitores r
LEFT JOIN emprestimos e ON e.leitor_id = r.id
GROUP BY r.id
ORDER BY total_emprestimos DESC;

-- 5. Livros que nunca foram emprestados
SELECT titulo, autor
FROM livros
WHERE id NOT IN (SELECT livro_id FROM emprestimos);
