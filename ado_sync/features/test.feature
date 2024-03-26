# language:pt
@suiteId:59
Funcionalidade: Teste de uma feature

@tc:68
@story:50
@ignore
Cenário: Derrubar no chão
Dado que o gato pulou na estante
Quando o gato encontrou um objeto
Então p gato derruba o objeto no chão

@tc:60
Esquema do Cenário: [Another Scenario] Isso é um teste
Dado que isso seja um teste do tipo <perfil>
E eu tenha um parametro de teste <teste>
Quando preencher todos os campos obrigatórios para executar o teste
Então o teste deverá ter passado

Exemplos:
| perfil | teste         |
| ADM    | administrador |
| Outro  | outro         |