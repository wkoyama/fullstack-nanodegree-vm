# Catálogo de itens

## Visão geral do projeto

Aplicativo que fornece uma lista de itens para uma variedade de categorias, bem como um sistema de registro e autenticação de usuários pelo Google, caso o usuário não exista ele registra o usuário automaticamente. Usuários registrados terão a capacidade de postar, editar e excluir suas próprias categorias e itens.


## Pré-Requisitos

**Necessário ter a vm do vagrant disponibilizado no curso**

**Para a configuração do ambiente em que esse projeto roda, seguir instruções nesse link: (Créditos a Udacity)**

1. Estamos usando ferramentas chamadas [Vagrant](https://www.vagrantup.com/) e [VirtualBox](https://www.virtualbox.org/wiki/Downloads) para instalar e gerenciar a VM.

    https://classroom.udacity.com/nanodegrees/nd004-br/parts/302d2209-30c1-4b9e-8615-2a1f4a5ee7c6/modules/e4147fc0-3658-48bf-8a6c-542fa272d0cd/lessons/5475ecd6-cfdb-4418-85a2-f2583074c08d/concepts/14c72fe3-e3fe-4959-9c4b-467cf5b7c3a0

2. Baixar o projeto:

    https://github.com/wkoyama/fullstack-nanodegree-vm.git

Após concluído a instalação do Vagrant e VirtualBox do passo 1, baixar o projeto e entrar na pasta fullstack-nanodegree-vm do passo 2 executar os seguintes passos:
 
- Iniciar a vm com `vagrant up` e entrar na VM com `vagrant ssh`
- Trocar para diretório /vagrant/catalog
- O ideal é ter 2 terminais abertos. No primeiro iniciar o servidor do Redis com o comando `redis-server &`
- No outro terminal, executar `python app.py`.
- Acessar e testar o aplicativo visitando http://localhost:5000 localmente