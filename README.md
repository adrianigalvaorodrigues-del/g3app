# De olho no custo — G3 Gestão

App de controle de orçamento e manutenção construído em Python com Streamlit.

## Instalação

```bash
pip install -r requirements.txt
```

## Executar

```bash
streamlit run app.py
```

O app abrirá automaticamente no navegador em `http://localhost:8501`

## Estrutura

```
g3app/
├── app.py              # Aplicação principal
├── requirements.txt    # Dependências
├── orcamento.xlsx      # Planilha de dados (padrão)
├── logo.jpg            # Logo G3
├── truck.png           # Foto do caminhão
└── diagrama.jpg        # Diagrama de manutenção
```

## Funcionalidades

- **Dashboard** — KPIs, 7 gráficos interativos Plotly
- **Unidades** — cards com resumo por unidade
- **Mão de Obra** — busca e ranking de custo/hora
- **Materiais** — 18.893 itens com filtros por unidade, fornecedor e CC
- **Equipamentos** — 350 equipamentos com filtros e gráficos

## Importar nova planilha

Use o botão "Importar Planilha" na sidebar para carregar um novo Excel.
A planilha deve ter as abas: `Unidades`, `mão de obra`, `MATERIAIS`, `Equipamentos`

## Deploy gratuito

1. Crie conta em https://streamlit.io/cloud
2. Faça upload do projeto no GitHub
3. Deploy com um clique
