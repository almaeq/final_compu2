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
```

4. Token de Hugging Face:
Iniciar sesión en Hugging Face, ir a settings y crear un token que sea FINEGRAINED. Solo marcar la opcion que dice "Read access to contents of all public gated repos you can access"

## Despliegue

1. Iniciar Redis:
```bash
redis-server 
```

2. Iniciar Celery:
```bash
celery -A server.ai_server worker --loglevel=info
```

3. Iniciar servidor:
```bash
# Entrar a la carpeta server
cd server
# Iniciar el servidor en ipv6
python ai_server.py --ipv4 "" --ipv6 "::" --port 8080
# Iniciar el servidor en ipv4
python ai_server.py --ipv4 "0.0.0.0" --ipv6 "" --port 8080
# Iniciar el servidor sin argumentos
python ai_server.py
```

4. Usar cliente:
```bash
# Entrar a la carpeta client
cd client
# Usar el cliente en ipv6
python client.py --server-url http://[::1]:8080
# Usar el cliente en ipv4
python client.py --server-url http://127.0.0.1:8080
# Usar el cliente sin argumentos
python client.py
```
