 Generador de Imágenes con IA

Sistema cliente-servidor para la generación de imágenes utilizando Stable Diffusion.

## 🚀 Características Principales

- 🖼️ Generación de imágenes mediante prompts de texto
- 🌐 Soporte dual IPv4/IPv6
- 📊 Sistema de cola distribuido
- 📝 Registro de actividades
- ⚡ Cliente asíncrono

## 📋 Uso Básico

### Iniciar el Servidor
```bash
# Iniciar Redis y Celery
redis-server --save "" --appendonly no
celery -A ai_server worker --loglevel=info

# Iniciar el servidor
python ai_server.py
```

### Usar el Cliente
```bash
python client.py
```
Sigue las instrucciones en pantalla para generar imágenes.

## 🛠️ Configuración

Argumentos del servidor:
```bash
python ai_server.py --ipv4 0.0.0.0 --ipv6 :: --port 8080
```

## 📁 Estructura

- `ai_server.py`: Servidor principal
- `client.py`: Cliente interactivo
- `generated_images/`: Imágenes generadas
- `server_log.txt`: Registro de actividades

Para instrucciones detalladas de instalación, consulta [INSTALL.md](INSTALL.md).