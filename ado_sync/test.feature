# language:pt
Funcionalidade: Anomalia de Agendamento Sem Checkin

@tc:68
@story:50
@ignore
Cenário: Derrubar no chão
    Dado que o gato pulou na estante
    Quando o gato encontrou um objeto
    Então p gato derruba o objeto no chão

@tc:69
@story:50
Cenário: Cenário 2
    Dado que o gato pulou na estante 1  
    Quando o gato encontrou um  asfasd
    Então p gato derruba o objeto no chão 3

@tc:1282308
Esquema do Cenário: [Negócio] - Criação de agendamento com sucesso
    Dado que esteja autenticado como <perfil>
    E navegar até opção de agendamento de carga <teste>
    Quando preencher todos os campos obrigatórios para criação de agendamento
    Então um novo agendamento de carga deverá ser criado com sucesso

    Exemplos:
    | perfil        |teste|
    | ADM           |a|
    | Supervisor TP |v|