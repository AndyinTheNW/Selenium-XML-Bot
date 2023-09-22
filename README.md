# Robô  - Automação DFE
### Observação:
**Esse código é um fragmento de um projeto privado maior, onde as outras etapas do processo são privadas.**

## Descrição do Projeto
Este projeto consiste em uma série de scripts Python para automatizar o processo de download, processamento e organização de arquivos XML e PDF. Os scripts usam bibliotecas como Tkinter, Selenium e Pdfminer para realizar tarefas de interface do usuário, automação de navegador da web e extração de texto de arquivos PDF, respectivamente.

Este código é um script Python que usa a biblioteca Selenium para automatizar interações no navegador web. Ele contém funções para configurar o driver do Chrome, fazer login em um site, baixar arquivos XML, processar os arquivos baixados e movê-los para diretórios específicos com base em certas condições.

O script executa as seguintes tarefas:
1. Configura o driver do Chrome com preferências personalizadas para baixar arquivos.
2. Faz login em um site usando as credenciais fornecidas.
3. Baixa arquivos XML para intervalos de datas especificados de dois servidores ("Server__RJ" e "Server__Brazil").
4. Processa os arquivos XML baixados, extraindo seus conteúdos e movendo-os para diretórios com base em determinadas condições.

## Pré-requisitos

- Python 3.x
- Biblioteca Selenium
- WebDriver do Google Chrome
- Configuração de preferências do navegador

