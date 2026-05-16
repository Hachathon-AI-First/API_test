# <img src="img/Símbolo Simplificado Roxo.png" alt="Logo Sauter" width=20 height=20> Sauter Digital 

Este projeto é uma aplicação em TypeScript que integra mensagens do WhatsApp, Google BigQuery, n8n e Salesforce. Ele fornece uma solução robusta e escalável para o gerenciamento e processamento de dados entre essas plataformas. O projeto foi projetado para ser altamente extensível, permitindo fácil personalização e a adição de novas funcionalidades.

## 🧠 Visão Geral da Arquitetura

![Arquitetura geral do projeto](./img/arquitetura-geral.png)

## 🎯 Objetivo do Projeto

O objetivo do projeto é centralizar, estruturar e resumir automaticamente conversas entre vendedores e clientes, transformando mensagens em insights acionáveis dentro do Salesforce, facilitando o acompanhamento do status das negociações.

Pontos centrais do projeto:
- Capturar todas as mensagens de conversas entre vendedores e clientes via WhatsApp
- Armazenar os dados de forma escalável e analítica no BigQuery
- Executar resumos periódicos automáticos das conversas
- Enviar os resumos estruturados para o Salesforce, permitindo:
1. Visualização do status da negociação
2. Histórico resumido da interação
3. Apoio à tomada de decisão comercial

## 🛠️ Tecnologias Utilizadas

- **TypeScript**: Um superset tipado do JavaScript que é compilado para JavaScript puro.
- **Node.js**: Um ambiente de execução JavaScript construído sobre o motor JavaScript V8 do Chrome.
- **Express**: Um framework web rápido, minimalista para Node.js.
- **Google Cloud BigQuery**: Um data warehouse em nuvem, serverless, altamente escalável e com excelente custo-benefício.
- **Google Cloud Pub/Sub**: Um serviço de mensageria para sistemas orientados a eventos e análises de streaming.
- **Terraform**: Uma ferramenta de infraestrutura como código (IaC) para criar, alterar e versionar infraestrutura de forma segura e eficiente.
- **N8N**: Uma ferramenta de automação de workflows que permite conectar diferentes serviços e construir fluxos complexos.
- **Jest**: Um framework de testes em JavaScript focado em simplicidade e boa experiência de desenvolvimento.
- **ESLint**: Uma ferramenta de linting configurável e extensível para identificar e reportar padrões problemáticos em JavaScript.

## 📦 Responsabilidades da Aplicação TypeScript

A aplicação principal é responsável por:
- Receber mensagens:
   - 📥 Mensagens recebidas de clientes
   - 📤 Mensagens enviadas por vendedores
- Normalizar e estruturar os dados da conversa
- Publicar eventos no **Google Pub/Sub**
- Garantir rastrabilidade e integridade das mensagens

## 📊 Estrutura dos Dados (Visão Geral)

Cada mensagem enviada ao Pub/Sub contém, de forma estruturada:
- Identificador da conversa
- Identificador do cliente
- Identificador do vendedor
- Conteúdo da mensagem
- Status da mensagem
- Timestamp
- Evento

Esses dados são persistidos no **BigQuery**, onde se tornam a base para análises e automações posteriores.

## 🔄 Processamento com n8n

- Um fluxo no n8n é executado a cada 3 dias
- O fluxo:
   - Consulta conversas no BigQuery
   - Agrupa mensagens por conversa
   - Envia o histórico da conversa para um **Vertex AI**
   - Gera um resumo estruturado, incluindo:
      - Contexto da conversa
      - Interesse do cliente
      - Tipo de interação
      - Status da negociação
      - Sugestões dos próximos passos para a negociação
   - Envia os dados para um objeto de Interação no Salesforce

## 🤖 Vertex AI - Resumo Estruturado e Associação com os dados do Salesforce

O projeto utiliza Vertex AI como componente central de inteligência no fluxo de processamento das conversas, sendo responsável por transformar mensagens brutas do WhatsApp em informações estruturadas e acionáveis no Salesforce.

No fluxo do n8n, são utilizados dois nodes distintos do Vertex AI, cada um com uma responsabilidade bem definida:

### 🧾 Geração de Resumos Estruturados da Conversa

O primeiro node do Vertex AI recebe o histórico completo da conversa, previamente agrupado e ordenado a partir dos dados armazenados no BigQuery.

Esse node é responsável por:

- Analisar o contexto da conversa entre vendedor e cliente
- Gerar um resumo estruturado, eliminando ruídos e mensagens irrelevantes
- Identificar pontos-chave da interação, como:
   - Interesse do cliente
   - Dúvidas ou objeções
   - Estágio da negociação
   - Próximos passos sugeridos

O resultado é um objeto estruturado, padronizado e pronto para consumo por sistemas downstream.

### ☁️ Associação com Dados do Salesforce e Persistência

O segundo node do Vertex AI atua na associação inteligente da conversa resumida com os dados existentes no Salesforce.

Esse node é responsável por:
- Correlacionar a conversa com entidades do Salesforce (como Contact ou Opportunity)
- Enriquecer os dados do resumo com informações de contexto comercial
- Estruturar o payload final de acordo com o modelo do Objeto de Interação no Salesforce
- Persistir os dados diretamente no Salesforce via integração com a API

Essa etapa garante que cada conversa esteja corretamente vinculada ao cliente e ao estágio comercial correspondente.

## 📂 Documentação

Para detalhes completos sobre cada componente e configuração do projeto, consulte a documentação mestre:

- *Documentação em construção*
