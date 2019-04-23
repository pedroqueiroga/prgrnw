OBJETIVO: Não atrasar mais entregas dos livros na biblioteca.

Lê de um arquivo chamado `credenciais`, que deve ser do formato:
```
cpf
senha
```
Entra no pergamum e insere essas credenciais, renova todos os livros que podem ser renovados naquele dia. Depois disso, cria jobs `at`, que serão executados nas novas datas de devolução de cada item renovado.

TODO: Enviar e-mail não-local (para uma conta de e-mail, por exemplo gmail), informando as coisas que imprime. No momento, vão parar no `/var/spool/mail/$USER` ou seja lá qual for o destino de e-mails locais, pois o `at` envia e-mails locais. (melhor confirmação de que conseguiu renovar)
TODO: Livro virar classe, e mais refactors que estão bem óbvios.
TODO: Tentar encontrar uma forma melhor de guardar as credenciais.
TODO: Escrever um e-mail melhor para quando não for possível renovar.(atrasado/precisa ser retornado)
TODO: Empacotar, para instalar dependências e tal (geckodriver -> selenium, at(?))