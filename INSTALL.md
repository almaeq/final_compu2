# 📥 Guía de Instalación y Despliegue

## Requisitos Previos

- Python 3.8+
- Redis Server
- Token de Hugging Face
- GPU compatible con CUDA (opcional)

## Instalación

1. Clonar repositorio:
```bash
git clone https://github.com/almaeq/final_compu2.git
cd final_compu2
```

2. Crear y activar entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
``

## Despliegue

1. Iniciar Redis:
```bash
redis-server --save "" --appendonly no
```

2. Iniciar Celery:
```bash
celery -A ai_server worker --loglevel=info
```

3. Iniciar servidor:
```bash
python ai_server.py
```

4. Usar cliente:
```bash
python client.py
```
