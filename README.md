 Generador de Imágenes con IA

Sistema cliente-servidor para la generación de imágenes utilizando Stable Diffusion.

## 🚀 Características Principales

- 🖼️ Generación de imágenes mediante prompts de texto
- 🌐 Soporte dual IPv4/IPv6 (las direcciones del servidor se pueden poner como parámetro o en el .env)
- 📊 Sistema de cola distribuido
- 📝 Registro de actividades
- 📦 Almacenamiento de imágenes
- 📝 Logging separado
- ⚡ Cliente asíncrono

## 📋 Uso Básico

### Iniciar el Servidor
```bash
# Iniciar Redis y Celery
redis-server --save "" --appendonly no
celery -A ai_server worker --loglevel=info

# Iniciar el servidor en ipv6
python ai_server.py --ipv4 "" --ipv6 "::" --port 8080
# Iniciar el servidor en ipv4
python ai_server.py --ipv4 "0.0.0.0" --ipv6 "" --port 8080
```                                                                                                                     

### Usar el Cliente
```bash
# Usar el cliente en ipv6 con la dirección del servidor
python client.py --server-url http://[::1]:8080
# Usar el cliente en ipv4 con la dirección del servidor
python client.py --server-url http://127.0.0.1:8080
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