# Roleforge-API

API para o aplicativo RoleForge, desenvolvido para o projeto integrado do 5° semestre do curso de Desenvolvimento 
de Software Multiplataforma da FATEC Mauá.

O RoleForge é um aplicativo mobile desenvolvido com o intuito de ser uma ferramenta auxiliar para jogadores de RPG de 
mesa, permitindo que mestres organizem suas campanhas, que jogadores tenham seus próprios personagens salvos, e muito 
mais.

## Características

* API na arquitetura REST;
* Desenvolvida no padrão MVC;
* Escrita em Python, versão 3.12;
* Conectada ao banco de dados MongoDB Atlas;
* Utiliza as bibliotecas Pydantic, Uvicorn, Fastapi, Pymongo e Python-dotenv;
* Hosteada na plataforma [Render](https://render.com).

## Como executar o projeto localmente
As bibliotecas listadas acima podem ser instaladas facilmente através do comando:

`pip install -r requirements.txt`

É necessário criar um arquivo `.env` no diretório raiz do projeto e configurar a variável de ambiente `DATABASE_URL` 
com a string de conexão do seu cluster no MongoDB Atlas.

Com a variável de ambiente configurada, é possível executar o projeto com o comando:

`python main.py`
