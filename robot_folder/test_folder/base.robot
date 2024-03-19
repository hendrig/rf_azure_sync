*Settings*
Documentation           Keywords GET do Load Scheduler
Library                 DateTime

*Variables*

*Keywords*

Dado que esteja autenticado como adm
    [return]                true

Quando enviar requisição GET
    [return]                true

Então o status code deverá ser 200 success
    [return]                true
    
E o response deverá retornar as informações
    [return]                true