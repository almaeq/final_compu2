import requests
import time
import os
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
import subprocess

# Cargar variables de entorno
load_dotenv()

# URL base del servidor
BASE_URL = os.getenv("SERVER_URL", "http://localhost:8080")

class ImageClient:    
    def __init__(self, base_url=BASE_URL):
        """Inicializa el cliente con la URL del servidor y crea una sesión HTTP."""
        self.base_url = base_url
        self.session = requests.Session()

    def request_image(self, prompt):
        """Envía un prompt al servidor y solicita la generación de una imagen."""
        try:
            response = self.session.post(f"{self.base_url}/generate", json={"prompt": prompt})
            response.raise_for_status()
            data = response.json()
            print(f"✅ Imagen en proceso | ID: {data['image_id']} | Task ID: {data['task_id']}")
            return data["task_id"], data["image_id"]
        except requests.exceptions.RequestException as e:
            print(f"❌ Error al solicitar imagen: {e}")
            return None, None

    def check_status(self, task_id):
        """Consulta el estado de una tarea en el servidor."""
        try:
            response = self.session.get(f"{self.base_url}/status/{task_id}")
            response.raise_for_status()
            data = response.json()
            print(f"📌 Estado de la tarea ({task_id}): {data['status']}")
            return data
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Error al consultar estado: {e}")
            return None

    def wait_for_image(self, task_id):
        """Consulta el estado de la tarea en intervalos hasta que la imagen esté lista."""
        print("⌛ Esperando a que la imagen se genere...")
        while True:
            status_data = self.check_status(task_id)
            if not status_data:
                return None

            if status_data["status"] == "Completado":
                return status_data["image_path"]

            time.sleep(3)

    def preview_image(self, image_id):
        """Descarga y muestra la imagen sin guardarla."""
        try:
            response = self.session.get(f"{self.base_url}/image/{image_id}", stream=True)
            if response.status_code == 404:
                print("❌ Imagen no encontrada en el servidor.")
                return None

            image = Image.open(BytesIO(response.content))

        # En lugar de `Image.show()`, usa `subprocess` para abrir con otro visor
            temp_path = f"/tmp/{image_id}.png"
            image.save(temp_path)  # Guarda la imagen temporalmente
            subprocess.run(["xdg-open", temp_path])  # Abrir con el visor predeterminado en Linux

            return response.content  # Devuelve los datos de la imagen
        except requests.exceptions.RequestException as e:
            print(f"❌ Error al obtener la imagen: {e}")
            return None

    def download_image(self, image_id, image_data):
        """Guarda la imagen generada en un archivo."""
        try:
        # Obtener la ruta desde el .env o usar "downloaded_images" como predeterminado
            save_dir = os.getenv("DOWNLOAD_PATH", "downloaded_images").strip()

        # Validar que no sea una ruta inválida
            if not save_dir or save_dir in [".", "./", "/", ""]:
                print("⚠️ Ruta de descarga inválida, usando la predeterminada: downloaded_images")
                save_dir = "downloaded_images"

        # Crear el directorio si no existe (evitar recursión infinita)
            if not os.path.exists(save_dir):
                os.makedirs(save_dir, exist_ok=True)

            save_path = os.path.join(save_dir, f"{image_id}.png")

            with open(save_path, "wb") as file:
                file.write(image_data)

            print(f"✅ Imagen descargada en: {save_path}")
            return save_path    
        except Exception as e:
            print(f"❌ Error al guardar la imagen: {e}")
            return None

    def close(self):
        """Cierra la sesión del cliente."""
        self.session.close()


if __name__ == "__main__":
    """
    Ejemplo de uso del cliente:
    1. Solicita al usuario un prompt para la imagen
    2. Envía la solicitud al servidor
    3. Espera a que la imagen se genere
    4. Muestra la imagen antes de descargarla
    5. Pregunta si se quiere guardar
    """
    client = ImageClient()

    # Solicitar generación de imagen
    prompt = input("📝 Introduce el prompt para la imagen: ")
    task_id, image_id = client.request_image(prompt)

    if task_id and image_id:
        # Esperar a que la imagen esté lista
        image_path = client.wait_for_image(task_id)
        if image_path:
            # Mostrar la imagen antes de descargarla
            image_data = client.preview_image(image_id)
            
            if image_data:
                # Preguntar si se quiere guardar la imagen
                save_option = input("💾 ¿Quieres descargar la imagen? (s/n): ").strip().lower()
                if save_option == "s":
                    client.download_image(image_id, image_data)
                else:
                    print("🚫 Imagen no descargada.")
        else:
            print("❌ No se pudo generar la imagen.")
    
    client.close()
