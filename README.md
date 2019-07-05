# OBJETIVO: Não mais atrasar entregas dos livros na biblioteca.

Lê de um arquivo chamado `credenciais`, que deve ser do formato:
```
cpf
senha
```
Entra no pergamum e insere essas credenciais, renova todos os livros que podem ser renovados naquele dia. Depois disso, cria jobs `at`, que serão executados nas novas datas de devolução de cada item renovado.

* TODO: Livro virar classe, e mais refactors que estão bem óbvios.
* TODO: Tentar encontrar uma forma melhor de guardar as credenciais.
* TODO: Empacotar, para instalar dependências e tal (geckodriver -> selenium, at(?))
