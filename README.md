# Como Rodar o Server em sua Maquina

obs: esse guia assume que voce ja tenha o docker e as bibliotecas auxliares do postgres instaladas em sua maquina e fora realizado em ambiente linux (arch linux)

O banco de dados roda isolado em um ambiente docker, abra um terminal, que digamos que seja o terminal 1:

inicia o docker.service caso esteja desligado

    sudo systemctl start docker 

navega ate a pasta onde ficara o banco de dados 

    cd server-medications/dbms

sobe o container do banco em segundo plano

    sudo docker-compose -f docker-compose-model.yml up -d

util para checagem que o container esta rodando

    sudo docker ps

Agora que o banco esta rodando em um terminal, abra um terminal 2, vamos preparar o ambiente python da aplicacao

navegue ate a pasta com o manager.py e venv

    cd server-medications/lembramed

ative o ambiente virtual

    source venv/bin/activate

baixe as dependecias caso seja a primeira vez rodando

    pip install -r ../requirements.txt

Com o venv ativo e as dependencias ja instaladas pelo pip em seu ambiente virtual

cria as tabelas do banco no docker

    python manage.py migrate

cria um superusuario para acessar a pagina de admin caso primeira vez acessando

    python manage.py createsuperuser

inicia o servidor para desenvolvimento

    python manage.py runserver

Enderecos de browser uteis para testar o servidor:

- Aplicacao (Frontend/API): http://127.0.0.1:8000/

- Painel Administrativo: http://127.0.0.1:8000/admin/

# Erros Comuns ao Rodar

Caso ja tenha rodado anteriormente sera necessario derrubar os volumes 'fantasmas' criados anteriormente e rodar o docker compose up novamente. Na pasta do docker-compose-model.yml rode:

    sudo docker compose -f docker-compose-model.yml down -v