# Text Studio API

Proyecto sencillo con backend en Python + FastAPI, frontend en HTML/CSS/JavaScript y almacenamiento remoto en Supabase.

## Qué hace
- Corrige gramática y estilo en español.
- Sugiere mejoras de oraciones.
- Genera texto completo a partir de un tema o idea.
- Guarda el historial de solicitudes en Supabase.

## Estructura
- `main.py`: Servidor FastAPI y lógica de OpenAI + Supabase.
- `index.html`: Interfaz web sencilla.
- `style.css`: Estilos para el frontend.
- `index.js`: Lógica del cliente y llamadas a la API.
- `requirements.txt`: Dependencias del proyecto.

## Requisitos
- Python 3.11+ recomendado
- Cuenta y clave de OpenAI
- Proyecto Supabase con tabla `history`

## Instalación
```bash
python -m venv .venv
source .venv/bin/activate    
pip install -r requirements.txt
```

## Configuración
Crea un proyecto en Supabase y una tabla llamada `history` con estos campos:
- `id`: integer, primary key, auto increment
- `mode`: text
- `prompt`: text
- `result`: text
- `created_at`: timestamp with time zone (opcinalmente con valor por defecto `now()`)

Exporta las variables de entorno:
```bash
export OPENAI_API_KEY="tu_api_key"
export SUPABASE_URL="https://<tu-proyecto>.supabase.co"
export SUPABASE_KEY="tu_anon_o_service_role_key"
# Windows PowerShell
$env:OPENAI_API_KEY="tu_api_key"
$env:SUPABASE_URL="https://<tu-proyecto>.supabase.co"
$env:SUPABASE_KEY="tu_anon_o_service_role_key"
```

También puedes crear un archivo `.env` con estas variables si usas `python-dotenv`.

## Ejecución
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Abre `http://localhost:8000` en tu navegador.

## Notas
- El historial se consulta en `GET /api/history`.
- Las peticiones se envían a `POST /api/process`.
- Usa `.gitignore` para evitar subir el entorno virtual y la base de datos.
