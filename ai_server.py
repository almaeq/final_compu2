import argparse
import asyncio
import signal
import json
import datetime
from aiohttp import web
from multiprocessing import Process, Queue
from celery import Celery
from pathlib import Path
from uuid import uuid4
from PIL import Image, ImageDraw, ImageFont
from diffusers import DiffusionPipeline
import torch
from huggingface_hub import login


# Configuración de Celery
celery_app = Celery(
    "image_tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1"
)
celery_app.autodiscover_tasks(["ai_server"])
# Directorio de imágenes generadas
IMAGE_STORAGE = Path("./generated_images")
IMAGE_STORAGE.mkdir(exist_ok=True)

class LoggerService:
    #Servicio de logging en un proceso separado para evitar bloqueos.
    def __init__(self, log_file="server_log.txt"):
        self.log_file = log_file

    def start(self):
        self.queue = Queue()
        self.process = Process(target=self._log_writer, args=(self.queue,))
        self.process.start()

    def stop(self):
        self.queue.put(None)  # Señal para detener el logger
        self.process.join()

    def log(self, data):
        """Registra los datos en la cola de logs."""
        self.queue.put(data)

    def _log_writer(self, queue):
        """Proceso separado para escribir logs sin bloquear el servidor."""
        while True:
            log_entry =  queue.get()
            if log_entry is None:
                break
            log_entry["timestamp"] = datetime.datetime.now().isoformat()
            with open(self.log_file, "a") as log_file:
                log_file.write(json.dumps(log_entry) + "\n")

# Cargar el modelo de Stable Diffusion (solo una vez)
login()
#MODEL_PATH = "models/diffusers/stable-diffusion-v1-5"
pipe = DiffusionPipeline.from_pretrained("stable-diffusion-v1-5/stable-diffusion-v1-5", torch_dtype=torch.float32)

# Usar GPU si está disponible, si no, usar CPU
device = "cuda" if torch.cuda.is_available() else "cpu"
pipe.to(device)

def create_image(prompt: str, file_path: str):
    """Genera una imagen con Stable Diffusion basada en un prompt."""
    print(f"🎨 Generando imagen con IA para: {prompt}")
    
    # Generar la imagen
    image = pipe(prompt, num_inference_steps=20, guidance_scale=7.5).images[0]  

    # Guardar la imagen
    image.save(file_path)

    print(f"✅ Imagen guardada en: {file_path}")

# Tarea de Celery
@celery_app.task(name="generate_image")
def generate_image(prompt: str, image_id: str):
    try:
        print(f"🖼️ Generando imagen para: {prompt}")  # Agregar print para ver si llega aquí
        output_path = IMAGE_STORAGE / f"{image_id}.png"
        create_image(prompt, output_path)
        print(f"✅ Imagen guardada en: {output_path}")  # Confirmación de guardado
        return str(output_path)
    except Exception as e:
        print(f"❌ Error en la generación de imagen: {e}")  # Ver el error exacto
        raise e  # Para que Celery lo registre como error

class ImageServer:
    #Servidor HTTP asíncrono con IPv4 e IPv6 para la generación de imágenes.
    def __init__(self, ipv4_addr, ipv6_addr, port, logger_service):
        self.ipv4_addr = ipv4_addr
        self.ipv6_addr = ipv6_addr
        self.port = port
        self.logger = logger_service
        self.app = web.Application()
        self._setup_routes()

    def _setup_routes(self):
        """Define las rutas del servidor."""
        self.app.router.add_post("/generate", self.handle_generate)
        self.app.router.add_get("/status/{task_id}", self.handle_status)
        self.app.router.add_get("/image/{image_id}", self.handle_download)

    async def start(self):
        #Inicia el servidor en IPv4 e IPv6.
        runner = web.AppRunner(self.app)
        await runner.setup()

        self.site_ipv4 = web.TCPSite(runner, self.ipv4_addr, self.port)
        await self.site_ipv4.start()
        print(f"✅ Servidor iniciado en IPv4: http://{self.ipv4_addr}:{self.port}")

        self.site_ipv6 = web.TCPSite(runner, self.ipv6_addr, self.port)
        await self.site_ipv6.start()
        print(f"✅ Servidor iniciado en IPv6: http://[{self.ipv6_addr}]:{self.port}")

    async def stop(self):
        """Detiene el servidor limpiamente."""
        print("⏹️  Apagando el servidor...")
        await self.site_ipv4.stop()
        await self.site_ipv6.stop()

    async def handle_generate(self, request):
        """Maneja la solicitud de generación de imágenes."""
        try:
            payload = await request.json()
            prompt = payload.get("prompt", "").strip()
            if not prompt:
                return web.json_response({"error": "Prompt vacío"}, status=400)

            image_id = str(uuid4())
            task = celery_app.send_task("generate_image", args=[prompt, image_id])

            log_entry = {"action": "generate", "prompt": prompt, "image_id": image_id, "task_id": task.id}
            self.logger.log(log_entry)

            return web.json_response({
                "message": "Imagen en proceso",
                "image_id": image_id,
                "task_id": task.id
            })
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def handle_status(self, request):
        """Consulta el estado de una tarea de generación de imágenes."""
        task_id = request.match_info["task_id"]
        task_result = celery_app.AsyncResult(task_id)

        status_map = {
            "PENDING": "En cola",
            "SUCCESS": "Completado",
            "FAILURE": "Error",
        }
        status = status_map.get(task_result.state, "Desconocido")

        response = {"status": status}
        if task_result.state == "SUCCESS":
            response["image_path"] = task_result.result

        return web.json_response(response)

    async def handle_download(self, request):
        """Devuelve la imagen generada si está disponible."""
        image_id = request.match_info["image_id"]
        image_path = IMAGE_STORAGE / f"{image_id}.png"

        if not image_path.exists():
            return web.json_response({"error": "Imagen no encontrada"}, status=404)

        return web.FileResponse(image_path)

async def run_server():
    """Ejecuta el servidor y maneja señales para su apagado limpio."""
    parser = argparse.ArgumentParser(description="Servidor de Generación de Imágenes")
    parser.add_argument("--ipv4", type=str, default="0.0.0.0", help="Dirección IPv4")
    parser.add_argument("--ipv6", type=str, default="::", help="Dirección IPv6")
    parser.add_argument("--port", type=int, default=8080, help="Puerto")
    args = parser.parse_args()

    logger_service = LoggerService()
    logger_service.start()

    server = ImageServer(args.ipv4, args.ipv6, args.port, logger_service)

    stop_signal = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_signal.set)

    try:
        await server.start()
        print("🟢 Servidor en ejecución. Presiona Ctrl+C para detenerlo.")
        await stop_signal.wait()
    finally:
        await server.stop()
        logger_service.stop()

if __name__ == "__main__":
    asyncio.run(run_server())
