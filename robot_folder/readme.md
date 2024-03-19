# Automação API com Robot Framework

## 1. Começando

Para executar este projeto você deve seguir os passos abaixo:

- Instalar [Python 3.9 com Pip](https://www.python.org/downloads/)
- No terminal execute `pip install -r requirements.txt` para instalar todas as dependências do projeto

## 2. Estrutura do projeto

</br>
<ul>
    <li>Tests: Cenários de testes separados por contexto</li>
    <li>Resources: Arquivos de estrutura do projeto
        <ul>
            <li>Factories: Arquivos usados para massa de dados</li>
            <li>Keywords: Lógica usada para executar ações em testes </li>
            <li>Schemas: Json Schema das APIS</li>
        </ul>
    </li>
</ul>

## 3. Execução

Existem tipos diferentes de execução:

#### 3.1 Executando todos os testes

Para executar todos os testes, pode ser utilizado o script:
`robot -d ./reports -x outputxunit.xml tests`

#### 3.2 Executando por tags

Para executar testes específicos, podem ser utilizadas tags.
Para isso, pode ser utilizado o script a seguir, apenas trocando `tag` pela tag desejada:
`robot -d ./reports -i tag tests`

## 4. Reports

- Todos os artefatos de execução podem ser encontrados em `./reports`
- [Clique aqui para acessar o relatório de execução]((https://dev.azure.com/AMBEV-SA/BLINDANDO/_test/analytics?definitionId=9259&contextType=build)

## 5. Dependências

Bibliotecas utilizadas:

- `robotframework-requests`
- `robotframework-jsonvalidator`
- `robot-mongodb-library`
- `"pymongo[srv]"`
- `robotframework-faker`
- `pyyaml`

## 6. Rodando em container.

Execute os seguintes comandos:

- `docker build -t my-robot .`
- `docker run -it --rm -v $(pwd)/test_folder/:/my_project my-robot bash -c 'robot -d ./reports -x outputxunit.xml tests/first.robot'`
