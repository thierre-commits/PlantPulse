# PlantPulse

Projeto full-stack para simulacao, persistencia, analise e visualizacao de sinais de plantas.

## Visao do projeto

O PlantPulse organiza um fluxo completo de dados:

- geracao de sinais simulados
- exportacao para CSV
- ingestao em PostgreSQL
- leitura e analise estatistica
- exposicao via API FastAPI
- visualizacao em dashboard web com Next.js

O foco do projeto e mostrar uma base clara, evolutiva e pronta para demonstracao em portfolio tecnico.

## Estrutura final

```text
PlantPulse/
|-- backend/
|   |-- app/
|   |-- data/
|   |-- database/
|   |-- data_processing/
|   |-- sensor_simulation/
|   |-- tests/
|   |-- .env.example
|   `-- requirements.txt
|-- frontend/
|   |-- app/
|   |-- components/
|   |-- lib/
|   |-- .env.local.example
|   |-- package.json
|   `-- tsconfig.json
`-- README.md
```

## Arquitetura

### Backend

O backend concentra a logica do projeto:

- conexao com PostgreSQL
- simulacao e ingestao de dados
- leitura dos sinais
- analise estatistica inicial
- API REST versionada em `/api/v1`

### Frontend

O frontend consome a API existente e mostra:

- grafico temporal de sinais
- cards com metricas chave
- resumo analitico
- filtros por quantidade de registros e `sensor_id`

## Tecnologias

### Backend

- Python
- FastAPI
- psycopg2
- PostgreSQL
- pytest

### Frontend

- Next.js (App Router)
- TypeScript
- TailwindCSS
- Recharts

## Funcionalidades principais

- simulacao de sinais plausiveis de sensores
- exportacao para CSV
- importacao em lote para PostgreSQL
- leitura recente dos dados com filtro opcional por sensor
- analise com tendencia, variabilidade e anomalias
- API padronizada e versionada
- dashboard com filtros, grafico e resumo interpretativo

## Fluxo completo de dados

1. Crie o banco PostgreSQL:

```sql
CREATE DATABASE plantpulse;
```

2. Aplique o schema inicial a partir da pasta `backend`:

```powershell
cd backend
psql -h localhost -U postgres -d plantpulse -f database/schema.sql
```

3. Gere o CSV simulado:

```powershell
python sensor_simulation/plant_signal_generator.py
```

4. Importe os dados do CSV para o PostgreSQL:

```powershell
python data_processing/insert_data.py
```

Durante a importacao, registros duplicados com o mesmo `sensor_id` e `signal_timestamp` sao ignorados pelo PostgreSQL.

5. Suba o backend:

```powershell
uvicorn app.main:app --reload
```

6. Suba o frontend em outro terminal:

```powershell
cd frontend
npm install
npm run dev
```

O comando `npm install` instala as dependencias e gera/atualiza o `package-lock.json` quando necessario.

7. Acesse o dashboard:

```text
http://localhost:3000/dashboard
```

## Como rodar o backend

1. Entre na pasta:

```powershell
cd backend
```

2. Crie e ative a venv:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Instale as dependencias:

```powershell
pip install -r requirements.txt
```

4. Crie o `.env`:

```powershell
Copy-Item .env.example .env
```

5. Configure as credenciais do PostgreSQL.

6. Se necessario, aplique o schema:

```powershell
psql -h localhost -U postgres -d plantpulse -f database/schema.sql
```

Para tabelas ja existentes, aplique a restricao de unicidade manualmente:

```sql
ALTER TABLE plant_signals
ADD CONSTRAINT plant_signals_sensor_timestamp_unique
UNIQUE (sensor_id, signal_timestamp);
```

7. Rode a API:

```powershell
uvicorn app.main:app --reload
```

Backend disponivel em:

- `http://127.0.0.1:8000/api/v1`
- `http://127.0.0.1:8000/docs`

## Como rodar o frontend

1. Em outro terminal:

```powershell
cd frontend
```

2. Instale as dependencias:

```powershell
npm install
```

3. Crie o `.env.local`:

```powershell
Copy-Item .env.local.example .env.local
```

4. Ajuste a URL da API, se necessario:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api/v1
```

5. Rode o dashboard:

```powershell
npm run dev
```

Frontend disponivel em:

- `http://localhost:3000/dashboard`

## UX do dashboard

O dashboard inclui:

- seletor de limite com 50, 100 e 200 registros
- filtro opcional por `sensor_id`
- botao de atualizacao manual
- recarga automatica ao mudar os parametros
- estados de loading, erro e ausencia de dados

## Proximos passos

- testes automatizados do frontend
- deploy do backend e do frontend
- filtros mais ricos por periodo
- comparacao entre sensores
- historico de importacoes

## Melhorias aplicadas nesta finalizacao

- separacao real entre `backend/` e `frontend/`
- eliminacao do conflito estrutural da pasta `app/`
- tipagem do frontend refinada para `AnalysisData | null`
- dashboard mais interativo e mais adequado para demonstracao
- README atualizado para apresentacao profissional
