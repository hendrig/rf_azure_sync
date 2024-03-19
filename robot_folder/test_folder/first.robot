*Settings*
Documentation           GET Load Scheduler

Resource                ./base.robot

*Test Cases*

#@tc:1234
#@suite:123123123
#@story:13231212
#@story:12312331
#@bug:123312312
#v1/dock-types/id
Cenário: Primeiro Titulo
    Dado que esteja autenticado como adm
    Quando enviar requisição GET
    Então o status code deverá ser 200 success
    E o response deverá retornar as informações

#@tc:1234
#@suite:123123123
#@story:13231212
#@story:12312331
#@bug:123312312
#v1/dock-types/id
Cenário: Titulo diferente
    Dado que esteja autenticado como adm
    Quando enviar requisição GET
    E o response deverá retornar as informações