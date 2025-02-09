# Generador de Imágenes con IA

Este proyecto implementa un sistema cliente-servidor para la generación de imágenes utilizando Stable Diffusion.

## Características

- 🖼️ Generación de imágenes mediante prompts de texto
- 🌐 Soporte para IPv4 e IPv6
- 📊 Sistema de cola con Celery y Redis
- 📝 Registro de actividades
- ⚡ Cliente asíncrono para solicitudes

## Requisitos Previos

- Python 3.8+
- Redis Server
- Torch
- Token de Hugging Face

## Instalación

1. Clonar el repositorio:

```bash
git clone https://github.com/almaeq/final_compu2.git
cd final_compu2
```

2. Instalar las dependencias:

```bash
pip install -r requirements.txt
```

3. Configurar el servidor de Redis:

```bash 
redis-server --save "" --appendonly no
```

4. Iniciar el worker de Celery:

```bash
celery -A tasks worker --loglevel=info
```

5. Iniciar el servidor:

```bash
python ai_server.py
```

### Usar el Cliente

```bash
python client.py
```

## Estructura del Proyecto

- `ai_server.py`: Servidor principal con la lógica de generación de imágenes
- `client.py`: Cliente para interactuar con el servidor
- `generated_images/`: Directorio donde se almacenan las imágenes generadas
- `server_log.txt`: Registro de actividades del servidor

## Configuración

El servidor acepta los siguientes argumentos:
- `--ipv4`: Dirección IPv4 (default: 0.0.0.0)
- `--ipv6`: Dirección IPv6 (default: ::)
- `--port`: Puerto (default: 8080)
