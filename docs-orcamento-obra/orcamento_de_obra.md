# 🏗️ Documentação: Módulo de Orçamentos de Obra

<!-- METADADOS ESTRUTURADOS -->
**Módulo:** Engenharia  
**Funcionalidade:** Orçamentos de Obra  
**Palavras-chave:** orçamento, obra, engenharia, construção civil, planejamento, custos, BDI, composições, insumos, serviços  
**Público-alvo:** Engenheiros, gestores de obra, orçamentistas  
**Última atualização:** Novembro 2025

---

## 📋 Visão Geral do Módulo Orçamentos de Obra

**O que é um Orçamento de Obra?**  
Um orçamento de obra é uma estimativa detalhada dos custos necessários para executar um projeto de construção civil. No sistema Koper, este módulo permite criar, gerenciar e analisar orçamentos completos, incluindo materiais, mão de obra, equipamentos e custos indiretos.

**Por que usar Orçamentos de Obra?**  
- Determinar a **viabilidade financeira** de projetos
- Calcular **previsão de gastos e lucros**
- Gerar **propostas comerciais** para clientes
- Criar **planejamentos de obra** baseados em custos
- Controlar **margem de lucro** e **competitividade**

**Pré-requisitos para criar um orçamento:**
1. [Etapas cadastradas](https://ajuda.koper.com.br/ajuda-koper/engenharia/cadastros-etapas)
2. [Serviços cadastrados](https://ajuda.koper.com.br/ajuda-koper/engenharia/cadastros-servicos)
3. [Composições cadastradas](https://ajuda.koper.com.br/ajuda-koper/engenharia/cadastros-composicoes)

---

## 🏠 Interface Principal de Orçamentos

### Como acessar a tela de Orçamentos?
**Caminho:** Koper → Engenharia → Orçamentos de Obra

### Funcionalidades da interface principal:
1. **Cadastrar novo orçamento** - Botão "+ Orçamento"
2. **Filtros por obra** - Seleção de projetos específicos
3. **Pesquisa direta** - Busca por nome de obras cadastradas
4. **Visualização em lista** - Código, Nome, Obra, Cliente, Data, Valor e Status

### Status de Orçamentos:
- **Obras próprias:** Status sempre "Aberto"
- **Obras para terceiros:** Aberto → Análise comercial → Aprovado → Vendido → Venda cancelada

**Importante:** Orçamentos com status "Venda cancelada" não permitem novas propostas comerciais.

### Estrutura de Obras no Orçamento

**Pergunta:** Como a estrutura da obra influencia o orçamento?

**Componentes da estrutura de obra:**
- **Blocos:** Grandes divisões da obra
- **Níveis/Andares:** Subdivisões por altura
- **Unidades:** Apartamentos, salas, lojas
- **Subunidades:** Cômodos (quartos, cozinha, sala, etc.)

**Impacto no orçamento:**
- Permite **orçamentação específica** por unidade
- Facilita **controle de custos** por área
- Possibilita **análises de produtividade** segmentadas
- Melhora **rastreabilidade** de recursos

**Associação de unidades:**
- **Unidades relacionadas:** Apartamentos com vagas de garagem
- **Áreas privativas:** Metragem exclusiva de cada unidade
- **Áreas comuns:** Espaços compartilhados do condomínio

**Benefício para orçamentação:** Maior precisão na distribuição de custos e melhor controle de margens por tipo de unidade.

---

## 📊 Diário de Obras e Documentação

### Integração com Diário de Obras

**Pergunta:** Como o orçamento se relaciona com o diário de obras?

**Preenchimento automático:**
O diário de obras é alimentado automaticamente com informações de:
- **Engenharia:** Dados do orçamento e planejamento
- **Compras:** Aquisições realizadas
- **Suprimentos:** Movimentações de estoque
- **Recursos Humanos:** Alocação de pessoal

**Informações adicionais manuais:**
- **Clima:** Condições meteorológicas do dia
- **Observações:** Notas sobre o andamento da obra
- **Arquivos:** Documentos, fotos, relatórios
- **Interações:** Registros de comunicação

**Acesso:** Obras → "Ver diário de obra" → "Mais detalhes" do dia desejado

---

### Diferença entre Obra Própria e Obra para Terceiros

**Obra Própria:**
- **Definição:** Quando você vai construir e incorporar a obra
- **Características:** Realiza a venda de unidades (apartamentos, casas, etc.)
- **Contexto comercial:** Múltiplas vendas por unidade
- **Status de orçamento:** Sempre "Aberto"
- **Exemplo:** Construção de edifício residencial para venda de apartamentos

**Obra para Terceiros:**
- **Definição:** Quando você executa a obra mas não incorpora
- **Características:** Venda da obra como um todo para um único cliente
- **Contexto comercial:** Contratação de serviços de construção
- **Status de orçamento:** Pode variar entre todos os status comerciais
- **Exemplo:** Construção de prédio comercial para empresa contratante

## 🏗️ Cadastro e Gestão de Obras

### Como cadastrar uma obra?

**Pergunta:** Qual é o processo completo para cadastrar uma nova obra?

**Passo a passo:**
1. **Acessar módulo:** Koper → Engenharia → Obras
2. **Criar nova obra:** Clique em "+ Obra"
3. **Escolher versão:**
   - **Sistema padrão:** Interface moderna e intuitiva
   - **Versão tradicional:** Interface clássica familiar

**Informações obrigatórias:**
- **Informações gerais:** Nome, tipo, descrição
- **Estrutura:** Blocos, andares, unidades
- **Endereço:** Localização completa da obra

### Gestão da estrutura da obra

#### Como adicionar nova estrutura (Bloco/Andar/Unidade)?

1. Acesse "Obras" no módulo Engenharia
2. Selecione a obra desejada
3. Vá em "Estrutura da obra" → "+ Estrutura"
4. **Escolha o tipo:**
   - **Bloco:** Grande divisão da obra
   - **Unidade:** Apartamento, sala, loja
   - **Nível/Andar:** Subdivisão por altura
5. Preencha as informações solicitadas
6. Clique em "Salvar"

#### Como associar duas unidades?

**Exemplo:** Apartamento + vaga de garagem

1. Selecione a unidade principal (apartamento)
2. Clique em "Editar"
3. Acesse "Unidades relacionadas"
4. Preencha as informações de associação
5. Clique em "+ Relacionamento"
6. **Para vagas de garagem:** Marque a opção específica
7. Concluir a edição

### Gestão de áreas e nomenclatura

#### Como editar áreas privativas e comuns?

1. Acesse "Obras" → Obra desejada
2. Vá em "Estrutura" → "Editar áreas"
3. **Selecione as unidades** que receberão as áreas
4. **Defina:**
   - **Área privativa:** Metragem exclusiva
   - **Área comum:** Metragem compartilhada
5. Salvar as alterações

#### Como alterar nome das unidades?

1. Vá em "Estrutura" → "Editar nomes unidades"
2. **Preencha novos nomes** conforme necessário
3. Concluir a edição

**Exemplo:** Alterar "Apto 101" para "Apartamento Garden 01"

### Gestão de subunidades

#### Como adicionar subunidades (cômodos)?

**Pergunta:** Como cadastrar quartos, cozinha, sala em uma unidade?

1. Selecione a unidade desejada
2. Clique em "Subunidades"
3. **Preencha informações:**
   - Nome do cômodo
   - Área específica
   - Características especiais
4. Salvar

**Observação:** Não há limite de subunidades por unidade.

### Operações adicionais

#### Como adicionar imagem à obra?

1. Acesse a obra desejada
2. Clique no quadrado "Sem imagem"
3. Selecione a imagem desejada
4. Upload automático

#### Como editar/excluir uma obra?

**Editar:**
- Selecione "Editar" na obra desejada
- Altere informações gerais, característica ou endereço

**Excluir:**
- Selecione "Excluir" na obra desejada
- Confirme a operação

**Atenção:** Exclusão de obra pode afetar orçamentos associados.

---

## 🔧 Como Cadastrar um Novo Orçamento

### Pergunta: Como criar um orçamento de obra no sistema?

**Passo a passo detalhado:**

1. **Acesse o módulo:** Koper → Engenharia → Orçamentos de Obra
2. **Clique em:** Botão "+ Orçamento"
3. **Escolha o tipo de estrutura:**
   - **Por Composições/Insumos:** Estrutura baseada em composições técnicas
   - **Por Serviços:** Estrutura baseada em serviços executivos

4. **Preencha as informações básicas:**
   - **Nome do orçamento** (obrigatório)
   - **Valor do BDI** em porcentagem (opcional)
   - **Obra associada** (opcional)
   - **Cliente** (opcional para obras próprias, obrigatório para terceiros)

5. **Selecione a base de preços:**
   - **Base SINAPI:** Preços oficiais do Sistema Nacional de Pesquisa de Custos e Índices da Construção Civil
   - **Base Própria:** Preços customizados da empresa
   - **Ambas:** Utilização mista (recomendado)

6. **Finalize:** Clique em "Salvar"

### Diferenças entre tipos de orçamento:

| Tipo | Descrição | Quando usar |
|------|-----------|-------------|
| **Composições/Insumos** | Estrutura técnica detalhada por insumos | Orçamentos precisos e analíticos |
| **Serviços** | Estrutura executiva por atividades | Orçamentos rápidos e práticos |

---

## 📊 Detalhes de um Orçamento

### Como visualizar detalhes de um orçamento?
Clique sobre qualquer orçamento na listagem principal para acessar a visão detalhada.

### Painéis disponíveis na tela de detalhes:

#### 1. **Painel Informações Gerais**
**O que mostra:** Dados básicos do orçamento, obra associada e resumo financeiro.

**Funcionalidades:**
- Visualizar detalhes da obra
- Acessar cadastro do cliente  
- Ver resumo de valores, BDI e descontos
- **Adicionar descontos** ao valor total

#### 2. **Painel Base de Origem**
**O que mostra:** Informações sobre a base de preços utilizada (SINAPI, Própria).

**Dados exibidos:**
- Nome da base
- Estado de referência
- Data de referência dos preços

#### 3. **Painel Itens do Orçamento**
**O que mostra:** Estrutura hierárquica completa do orçamento.

**Funcionalidades:**
- Adicionar/editar **etapas**
- Adicionar/editar **subetapas**  
- Adicionar/editar **serviços, composições e insumos**
- Aplicar **BDI específico** por item
- Gerenciar **sequência e organização**

#### 4. **Painel Lista de Composições**
**O que mostra:** Todas as composições utilizadas no orçamento.

**Informações exibidas:**
- Código e descrição
- Origem (SINAPI/Própria)
- Quantidade total
- Valor unitário da origem vs. valor orçado
- **Percentual de diferença** entre valores

#### 5. **Painel Lista de Insumos**
**O que mostra:** Consolidação de todos os insumos do orçamento.

**Funcionalidades:**
- **Editar valores unitários** (SINAPI e Própria)
- Filtrar por tipo (Material, Mão de obra, Equipamento, Outros)
- Pesquisar insumos específicos
- Ver **resumo financeiro** por categoria

**Dados do resumo:**
- Valor total de insumos
- Número total de registros
- Distribuição por tipo de insumo

#### 6. **Painel Comercial** (apenas para obras de terceiros)
**O que mostra:** Gestão de propostas e vendas.

**Funcionalidades:**
- Gerar **propostas comerciais**
- Fazer **venda direta**
- Acompanhar status comercial

---

## 💰 Gestão de BDI (Benefícios e Despesas Indiretas)

### O que é BDI?
**BDI** é uma taxa aplicada ao custo direto da obra para cobrir:
- Despesas indiretas da construção
- Risco do empreendimento  
- Despesas financeiras
- Tributos incidentes
- Despesas de comercialização
- Lucro do empreendedor

### Como editar BDI no orçamento?

#### BDI Geral (todo o orçamento):
1. Acesse os detalhes do orçamento
2. Clique em "Editar" no painel superior
3. Altere o campo "Valor do BDI (%)"
4. Clique em "Concluir edição"

#### BDI Específico (item individual):
1. No painel "Itens do orçamento"
2. Localize o item (etapa, subetapa, serviço, composição ou insumo)
3. Clique no ícone de edição na coluna "BDI(R$)"
4. Defina valor exato ou porcentagem
5. Clique em "Concluir edição"

---

## 📝 Gestão de Etapas, Subetapas e Serviços

### Como adicionar uma etapa?

**Pergunta:** Como organizar o orçamento em etapas de execução?

1. Acesse os detalhes do orçamento
2. No painel "Itens do Orçamento", clique em "+ Etapa"
3. **Selecione uma etapa existente** ou **crie uma nova**
4. Para criar nova: clique em "+" e defina nome e sequência
5. Clique em "Salvar"

### Como adicionar uma subetapa?

1. Localize a etapa desejada
2. Clique no ícone de opções (⋮)
3. Selecione "Adicionar subetapa"
4. Escolha subetapa existente ou crie nova
5. Clique em "Salvar"

### Como adicionar serviços?

**Para orçamentos tipo "Serviços":**
1. Localize a etapa/subetapa
2. Clique no ícone de opções (⋮)
3. Selecione "Adicionar serviço"
4. Escolha base de origem (SINAPI/Própria)
5. Selecione o serviço ou crie novo
6. **Associe uma composição** (obrigatório)
7. Informe a quantidade
8. Clique em "Salvar"

### Como associar composição a serviço diretamente no orçamento?

**Pergunta:** Como vincular uma composição a um serviço durante a criação do orçamento?

**Processo detalhado:**
1. Acesse "Orçamentos de Obra" no módulo Engenharia
2. Selecione o orçamento desejado
3. Clique nos "3 pontinhos" (⋮) na etapa/subetapa desejada
4. Selecione "Adicionar serviço"
5. Escolha ou crie o serviço desejado
6. No campo "Selecione uma composição", clique em "+ Associar composição ao serviço"
7. **Selecione a base de origem:**
   - **Base Própria:** Composições customizadas da empresa
   - **Base SINAPI:** Composições oficiais do sistema nacional
8. Selecione a composição desejada
9. **Se a composição não existir:** Use "+ Adicionar" para criar nova composição

**Vantagem:** Permite associação dinâmica durante o processo de orçamentação, sem necessidade de cadastros prévios.

---

**Para orçamentos tipo "Composições/Insumos":**
1. Localize a etapa/subetapa
2. Clique no ícone de opções (⋮)
3. Selecione "Adicionar composição"
4. Escolha base de origem
5. Selecione composição ou crie nova
6. Informe quantidade
7. Associe serviço (opcional)
8. Clique em "Salvar"

### Como adicionar insumos?

1. Localize a etapa/subetapa
2. Clique no ícone de opções (⋮)
3. Selecione "Adicionar insumo"
4. Escolha base (SINAPI/Própria)
5. Selecione insumo ou crie novo
6. Para base SINAPI: opção de associar à base própria
7. Informe quantidade
8. Clique em "Salvar"

---

## ✏️ Edição de Itens do Orçamento

### Como editar informações de etapas?

**Pergunta:** Como modificar uma etapa já cadastrada no orçamento?

1. Localize a etapa no painel "Itens do Orçamento"
2. Clique no ícone de opções (⋮)
3. Selecione "Editar informações"
4. Altere **sequência** e/ou **nome da etapa**
5. Clique em "Concluir edição"

**Atenção:** Alterações no nome afetam **todos os orçamentos** que usam esta etapa.

### Como editar serviços cadastrados?

**Disponível apenas para orçamentos tipo "Serviços":**
1. Localize o serviço
2. Clique no ícone de opções (⋮)
3. Selecione "Editar informações"
4. Altere: sequência, composição associada, quantidade
5. Para alterar itens da composição: clique em "Alterar itens"
6. Clique em "Concluir edição"

**Importante:** Alterações em itens criam uma **nova composição** na base própria.

### Como editar composições?

**Disponível apenas para orçamentos tipo "Composições/Insumos":**
1. Localize a composição
2. Clique no ícone de opções (⋮)
3. Selecione "Editar informações"
4. Altere: sequência, serviço associado, quantidade
5. Para alterar itens: clique em "Alterar itens"
6. Clique em "Concluir edição"

### Como editar insumos?

1. Localize o insumo
2. Clique no ícone de opções (⋮)  
3. Selecione "Editar informações"
4. Altere: sequência, quantidade, valor unitário
5. Para insumos SINAPI: alterar associação à base própria
6. Clique em "Concluir edição"

---

## 🗑️ Exclusão de Itens

### Como excluir etapas, subetapas, serviços, composições ou insumos?

**Processo universal para exclusão:**
1. Localize o item no painel "Itens do Orçamento"
2. Clique no ícone de opções (⋮)
3. Selecione "Excluir item"
4. Confirme clicando em "OK"

**Atenção:** A exclusão remove permanentemente o item do orçamento.

---

## 💵 Gestão de Valores e Descontos

### Como editar valores unitários de insumos?

**Pergunta:** Como atualizar preços de insumos no orçamento?

1. Acesse o painel "Lista de Insumos"
2. Clique em "Editar valores unitários"
3. **Campos ficam editáveis** na coluna "VAL. UNIT. ORÇ."
4. Faça as alterações necessárias
5. Clique em "Salvar todos"

### Escopo de alterações de valores de insumos

**Pergunta:** Quando altero o valor de um insumo, onde essa mudança se aplica?

**Alteração no orçamento (escopo limitado):**
- **Onde alterar:** Painel "Lista de insumos" → "Editar valores unitários"
- **Impacto:** Apenas no orçamento atual
- **Uso recomendado:** Ajustes específicos para um projeto particular

**Alteração global (escopo amplo):**
- **Onde alterar:** Diretamente no cadastro do insumo
- **Impacto:** Todos os novos orçamentos criados
- **Uso recomendado:** Atualização de preços de mercado

**Importante:** Alterações em orçamentos não afetam o cadastro base dos insumos.

---

1. No painel "Informações Gerais"
2. Localize o campo de valores
3. Em "Descontos", clique no ícone de edição (✏️)
4. Adicione **valor absoluto** ou **porcentagem**
5. Clique em "Salvar"

**Visualização:** O desconto aparece ao lado do valor total na listagem principal.

---

## 📋 Operações Avançadas de Orçamento

### Como replicar um orçamento?

**Pergunta:** Como copiar um orçamento existente para criar um novo?

1. Acesse os detalhes do orçamento
2. Clique no botão "Replicar" no painel superior
3. **Defina o nome** do novo orçamento
4. Opcionalmente, associe **obra e cliente diferentes**
5. Clique em "Salvar"

**Nome padrão:** "Cópia (nome do orçamento original)"

### Como excluir um orçamento?

1. Acesse os detalhes do orçamento
2. Clique no botão "Excluir" no painel superior
3. Confirme a exclusão clicando em "OK"

**Atenção:** Esta ação é **irreversível**.

### Como gerar planejamento a partir do orçamento?

1. Acesse os detalhes do orçamento
2. Clique em "Gerar planejamento"
3. Defina o **nome do planejamento**
4. **Associe uma obra** (obrigatório)
5. Opcionalmente, associe um cliente
6. Clique em "Salvar"

**Resultado:** Cria um [Planejamento de obra](https://ajuda.koper.com.br/ajuda-koper/engenharia/planejamento-de-obra) baseado no orçamento.

---

## 📊 Relatórios de Orçamento

### Que tipos de relatórios podem ser gerados?

**Pergunta:** Quais relatórios estão disponíveis para orçamentos de obra?

**Como gerar relatórios:**
1. Acesse os detalhes do orçamento
2. Clique no botão "Relatórios" (📄)
3. Selecione o tipo desejado

### Tipos de relatórios disponíveis:

| Relatório | Descrição | Quando usar |
|-----------|-----------|-------------|
| **Orçamento (com BDI em todos os itens)** | BDI aplicado individualmente em cada item | Apresentação detalhada para clientes |
| **Orçamento (com BDI apenas sobre o total)** | BDI aplicado somente no valor final | Orçamentos sintéticos |
| **Orçamento (com BDI não apresentado)** | BDI incluído mas não exibido separadamente | Orçamentos "limpos" sem detalhamento |
| **Orçamento analítico** | Detalhamento completo de insumos por serviço | Análise técnica e conferência |
| **Lista de insumos** | Consolidação de todos os materiais | Compras e suprimentos |
| **Lista de composições** | Relação de composições utilizadas | Análise de produtividade |
| **Curva ABC de insumos** | Análise de representatividade dos materiais | Gestão estratégica de estoque |
| **Curva ABC de serviços** | Análise de representatividade dos serviços | Planejamento executivo |

**Formato:** Todos os relatórios são gerados em **PDF**.

---

## 💼 Módulo Comercial (Obras para Terceiros)

### Como gerar proposta comercial?

**Pergunta:** Como criar uma proposta comercial a partir de um orçamento?

**Disponível apenas para:** Orçamentos sem obra associada ou com obras para terceiros.

**Passo a passo:**
1. Acesse o painel "Comercial"
2. Clique em "+ Proposta" no painel "Propostas Comerciais"
3. **Associe um cliente** (obrigatório)
4. Opcionalmente, associe uma obra
5. Clique em "Próximo"
6. Configure as **condições de pagamento**
7. Clique em "Salvar"

### Condições especiais de pagamento:

#### Para entrada personalizada:
1. No painel "ENTRADA", clique em "Condição especial"
2. Configure **parcelas de reforço**
3. Defina **parcelamento customizado**
4. Adicione **indexadores** se necessário
5. Configure **gatilhos** para consolidação
6. Escolha **tipo de juros**
7. Clique em "Salvar"

#### Para financiamento com a construtora:
1. No painel "SALDO CONSTRUTORA", clique em "Condição especial"
2. Siga o mesmo processo da entrada
3. Configure condições específicas do financiamento

**Funcionalidade avançada:** "Ver simulação de parcelamento" para prévia das parcelas.

### Como fazer venda direta?

**Pergunta:** Como registrar uma venda direta sem proposta prévia?

**Uso recomendado:** Vendas já concretizadas ou cadastros históricos.

1. Acesse o painel "Comercial"
2. Clique em "Venda direta"
3. Defina **classificação** da venda
4. **Associe cliente** (obrigatório)
5. Opcionalmente, associe obra
6. Defina **data da venda**
7. Clique em "Próximo"
8. Configure condições de **pagamento**
9. Escolha opção de contas no financeiro:
   - "Adicionar todas as contas"
   - "Adicionar apenas contas a partir de [data]"
10. Clique em "Salvar"

## 💼 Processo de Venda Completo

### Modalidades de venda de orçamentos

**Pergunta:** Quais são as formas de vender um orçamento no sistema?

O sistema oferece **duas modalidades principais** de venda:

#### **1. Venda com Contrato (Processo Formal)**

**Quando usar:** Vendas formais que requerem documentação legal e acompanhamento detalhado.

**Fluxo completo:**
1. **Criar proposta:** Orçamento → Comercial → "+ Proposta"
2. **Configurar condições:** Definir cliente e condições de pagamento
3. **Aprovação:** Proposta deve ser aprovada internamente
4. **Gerar contrato:** Após aprovação, gerar documento legal
5. **Assinatura:** Contrato deve ser assinado pelas partes
6. **Venda concretizada:** Status muda para "Vendido" automaticamente

**Características:**
- **Rastreabilidade completa** do processo
- **Documentação legal** gerada automaticamente
- **Controle de aprovações** e workflows
- **Integração** com contas a receber

#### **2. Venda Direta (Processo Simplificado)**

**Quando usar:** Vendas já concretizadas, registros históricos ou processos informais.

**Fluxo simplificado:**
1. **Acessar comercial:** Orçamento → Comercial → "+ Venda"
2. **Configurar condições:** Definir cliente e condições de pagamento
3. **Salvar:** Venda é registrada imediatamente

**Características:**
- **Processo imediato** sem aprovações
- **Não gera contrato** formal
- **Ideal para registros** de vendas já realizadas
- **Configuração flexível** de condições

### Qual modalidade escolher?

| Critério | Com Contrato | Venda Direta |
|----------|-------------|--------------|
| **Formalização** | Alta | Baixa |
| **Controle** | Rigoroso | Flexível |
| **Documentação** | Completa | Simplificada |
| **Tempo de processo** | Mais longo | Imediato |
| **Uso recomendado** | Vendas futuras | Registros históricos |

---

## 🔄 Fluxo Completo de Status Comercial

### Sequência para obras de terceiros:

1. **Orçamento criado** → Status: "Aberto"
2. **Proposta gerada** → Status: "Análise comercial"
3. **Proposta aprovada** → Status: "Aprovado"
4. **Contrato assinado** → Status: "Vendido"
5. **Venda cancelada** → Status: "Venda cancelada"

### Integração com outros módulos:

**Após venda concretizada:**
- **Contas a Receber:** Parcelas geradas automaticamente
- **Comissões:** Cálculo para equipe de vendas
- **Aditivos:** Possibilidade de alterações contratuais
- **Análise Financeira:** Classificação da venda

---

## 🔄 Integração com Outros Módulos

### Fluxo de Engenharia Completo

**Pergunta:** Como o orçamento se integra com outros módulos da engenharia?

**Sequência recomendada:**
1. **Obras:** Cadastro da obra (própria ou terceiros)
2. **Orçamentos:** Criação do orçamento detalhado
3. **Planejamento:** Geração do planejamento baseado no orçamento
4. **Acompanhamento:** Execução e controle da obra
5. **Medições:** Para contratos com prestadores de serviços
6. **Finalização:** Encerramento da obra

### Integração com Acompanhamento de Obra

**Como adicionar produto no acompanhamento que não foi orçado?**

**Método 1 - Edição de serviço:**
1. Acesse o acompanhamento da obra
2. Localize o serviço relacionado
3. Edite o serviço incluindo o novo recurso

**Método 2 - Associação na compra:**
1. Durante o processo de solicitação/compra
2. Indique o serviço onde o novo recurso será utilizado
3. O sistema associará automaticamente

### Integração com Contratos e Medições

**Processo para medições a pagar:**

**Pré-requisitos:**
- Engenharia completa (orçamento → acompanhamento)
- Contrato assinado com prestador de serviços

**Fluxo de medições:**
1. **Criar contrato:** No acompanhamento de obras
2. **Assinar contrato:** Formalização legal
3. **Editar medição:** Inserir quantidades medidas vs. planejadas
4. **Finalizar medição:** Aprovação dos valores
5. **Liberação financeira:** Gerar contas a pagar no módulo financeiro

### Finalização de Obra

**Pergunta:** Quais são os requisitos para finalizar uma obra?

**Pré-condições obrigatórias:**
- **Estoque zerado:** Nenhum produto em estoque da obra
- **Sem transferências pendentes:** Todas as movimentações concluídas
- **Sem colaboradores alocados:** Desalocação completa da equipe

**Processo:**
1. Acesse "Obras" no módulo Engenharia
2. Selecione a obra desejada
3. Altere o status para "Finalizada"
4. Sistema valida automaticamente as pré-condições

---

## 🎯 Glossário de Termos

| Termo | Definição | Contexto de uso |
|-------|-----------|-----------------|
| **BDI** | Benefícios e Despesas Indiretas - taxa sobre custos diretos | Formação de preço final |
| **Bloco** | Grande divisão estrutural da obra (Bloco A, B, C) | Organização de estrutura de obra |
| **Composição** | Conjunto de insumos para executar uma unidade de serviço | Orçamentação técnica |
| **Etapa** | Divisão macro do orçamento por fase da obra | Organização estrutural |
| **Insumo** | Material, mão de obra ou equipamento básico | Componente básico de custo |
| **Medição** | Processo de quantificar serviços executados para pagamento | Contratos com prestadores |
| **Nível/Andar** | Subdivisão da obra por altura (Térreo, 1º andar) | Estrutura vertical da obra |
| **Obra própria** | Construção para incorporação e venda de unidades | Empreendimento imobiliário |
| **Obra para terceiros** | Construção sob contrato para cliente específico | Prestação de serviços |
| **SINAPI** | Sistema Nacional de Pesquisa de Custos e Índices | Base oficial de preços |
| **Subetapa** | Subdivisão de uma etapa | Detalhamento organizacional |
| **Subunidade** | Cômodos dentro de uma unidade (quarto, sala, cozinha) | Detalhamento de unidades |
| **Serviço** | Atividade executiva da construção | Unidade de execução |
| **Unidade** | Subdivisão da obra para venda/uso (apartamento, sala) | Produto final da obra |
| **Unidades relacionadas** | Associação entre unidades (apartamento + vaga) | Gestão de vendas casadas |
| **Venda direta** | Modalidade de venda sem geração de contrato | Registro simplificado de vendas |

---

## 🔍 Perguntas Frequentes (FAQ)

### P: Posso alterar o tipo de orçamento depois de criado?
**R:** Não. Para mudar de "Composições/Insumos" para "Serviços" ou vice-versa, é necessário criar um novo orçamento.

### P: Como funciona a diferença entre valores SINAPI e orçado?
**R:** O sistema calcula automaticamente o percentual de diferença entre o valor da base SINAPI e o valor que você definiu no orçamento, permitindo análise de competitividade.

### P: Posso usar bases SINAPI e Própria no mesmo orçamento?
**R:** Sim. Você pode mesclar insumos de ambas as bases conforme necessário.

### P: O que acontece quando altero uma etapa ou composição?
**R:** Alterações em nomes de etapas e composições afetam **todos os orçamentos** que as utilizam.

### P: Como controlar margens de lucro?
**R:** Use o BDI para definir margens sobre custos diretos. Analise relatórios de Curva ABC para focar nos itens de maior impacto.

### P: Qual a diferença entre obra própria e obra para terceiros?
**R:** Obra própria é para incorporação e venda de unidades (apartamentos). Obra para terceiros é prestação de serviços de construção para um cliente específico.

### P: Como associar uma composição a um serviço durante o orçamento?
**R:** Use o menu de 3 pontinhos na etapa/subetapa → "Adicionar serviço" → "Selecione uma composição" → "+ Associar composição ao serviço".

### P: Alterações de valores de insumos afetam outros orçamentos?
**R:** Não. Alterações no painel "Lista de insumos" afetam apenas o orçamento atual. Para alterações globais, edite diretamente o cadastro do insumo.

### P: Como adicionar um produto no acompanhamento que não foi orçado?
**R:** Edite o serviço no acompanhamento incluindo o novo recurso, ou indique o serviço durante a solicitação/compra.

### P: Quais são os pré-requisitos para finalizar uma obra?
**R:** Estoque zerado, sem transferências pendentes e sem colaboradores alocados na obra.

### P: Existe limite para subunidades (cômodos) em uma unidade?
**R:** Não há limite. Você pode adicionar quantas subunidades desejar (quartos, salas, cozinhas, etc.).

### P: Como funciona o diário de obras em relação ao orçamento?
**R:** O diário é preenchido automaticamente com dados de engenharia, compras, suprimentos e RH. Você pode adicionar informações manuais como clima e observações.

---

## 📞 Suporte e Documentação Adicional

**Documentações relacionadas:**
- [Cadastros - Etapas](https://ajuda.koper.com.br/ajuda-koper/engenharia/cadastros-etapas)
- [Cadastros - Serviços](https://ajuda.koper.com.br/ajuda-koper/engenharia/cadastros-servicos)  
- [Cadastros - Composições](https://ajuda.koper.com.br/ajuda-koper/engenharia/cadastros-composicoes)
- [Planejamento de obra](https://ajuda.koper.com.br/ajuda-koper/engenharia/planejamento-de-obra)

**Módulos integrados:**
- **Compras:** Para aquisição de insumos orçados
- **Suprimentos:** Para controle de estoque
- **Financeiro:** Para gestão de recebimentos
- **Vendas:** Para propostas comerciais

---

## 📋 Resumo das Funcionalidades Principais

### Criação e Gestão de Orçamentos
- ✅ Cadastro com duas estruturas (Composições/Insumos ou Serviços)
- ✅ Integração com obras próprias e para terceiros
- ✅ Gestão de BDI geral e específico por item
- ✅ Associação dinâmica de composições a serviços

### Estrutura e Organização
- ✅ Hierarquia completa: Etapas → Subetapas → Serviços/Composições/Insumos
- ✅ Gestão de estrutura de obra (blocos, andares, unidades, subunidades)
- ✅ Edição de áreas privativas e comuns
- ✅ Associação de unidades relacionadas

### Precificação e Análise
- ✅ Edição de valores unitários com escopo controlado
- ✅ Relatórios diversificados (analíticos, curvas ABC, listas)
- ✅ Comparação automática entre bases SINAPI e própria
- ✅ Gestão de descontos no valor total

### Processo Comercial
- ✅ Duas modalidades de venda (com contrato e venda direta)
- ✅ Propostas comerciais com condições especiais
- ✅ Controle de status comercial completo
- ✅ Integração com contas a receber

### Integração com Módulos
- ✅ Geração de planejamento baseado no orçamento
- ✅ Integração com acompanhamento de obra
- ✅ Processo de medições e contratos
- ✅ Diário de obras automatizado
- ✅ Finalização controlada de obras

---

*Este documento serve como **base de conhecimento** para uso em sistemas de **RAG (Retrieval-Augmented Generation)**, facilitando a busca semântica e automação de respostas sobre orçamentos de obra no sistema Koper.*
