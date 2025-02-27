import requests
import time
import os
from dotenv import load_dotenv

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

    def download_image(self, image_id, save_dir=os.getenv("DOWNLOAD_PATH", "downloaded_images")):
        """Descarga una imagen generada por el servidor."""
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, f"{image_id}.png")

        try:
            response = self.session.get(f"{self.base_url}/image/{image_id}", stream=True)
            if response.status_code == 404:
                print("❌ Imagen no encontrada en el servidor.")
                return None

            with open(save_path, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)

            print(f"✅ Imagen descargada en: {save_path}")
            return save_path
        except requests.exceptions.RequestException as e:
            print(f"❌ Error al descargar la imagen: {e}")
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
    4. Descarga la imagen generada
    """
    client = ImageClient()

    # Solicitar generación de imagen
    prompt = input("📝 Introduce el prompt para la imagen: ")
    task_id, image_id = client.request_image(prompt)

    if task_id and image_id:
        # Esperar a que la imagen esté lista
        image_path = client.wait_for_image(task_id)
        if image_path:
            # Descargar imagen
            client.download_image(image_id)
        else:
            print("❌ No se pudo generar la imagen.")
    
    client.close()
