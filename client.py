import requests
import time
import os
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
import subprocess
import argparse

load_dotenv()

def get_client_config():
    parser = argparse.ArgumentParser(description="Cliente de generación de imágenes")

    server_url_env = os.getenv("SERVER_URL")

    parser.add_argument("--server-url", type=str, default=server_url_env if server_url_env else "http://localhost:8080",
                        help="URL del servidor (IPv4 o IPv6)")

    return parser.parse_args()

class ImageClient:    
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()

    def request_image(self, prompt):
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
        print("⌛ Esperando a que la imagen se genere...")
        while True:
            status_data = self.check_status(task_id)
            if not status_data:
                return None

            if status_data["status"] == "Completado":
                return status_data["image_path"]

            time.sleep(3)

    def preview_image(self, image_id):
        try:
            response = self.session.get(f"{self.base_url}/image/{image_id}", stream=True)
            if response.status_code == 404:
                print("❌ Imagen no encontrada en el servidor.")
                return None

            image = Image.open(BytesIO(response.content))
            temp_path = f"/tmp/{image_id}.png"
            image.save(temp_path)
            subprocess.run(["xdg-open", temp_path])

            return response.content
        except requests.exceptions.RequestException as e:
            print(f"❌ Error al obtener la imagen: {e}")
            return None

    def download_image(self, image_id, image_data, save_dir):
        try:
            if not save_dir or save_dir in [".", "./", "/", ""]:
                print("⚠️ Ruta de descarga inválida, usando la predeterminada: downloaded_images")
                save_dir = "downloaded_images"

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
        self.session.close()

if __name__ == "__main__":
    args = get_client_config()
    download_path = os.getenv("DOWNLOAD_PATH", "downloaded_images").strip()

    client = ImageClient(base_url=args.server_url)

    try:
        prompt = input("📝 Introduce el prompt para la imagen: ")
        task_id, image_id = client.request_image(prompt)

        if task_id and image_id:
            image_path = client.wait_for_image(task_id)
            if image_path:
                image_data = client.preview_image(image_id)

                if image_data:
                    save_option = input("💾 ¿Quieres descargar la imagen? (s/n): ").strip().lower()
                    if save_option == "s":
                        client.download_image(image_id, image_data, download_path)
                    else:
                        print("🚫 Imagen no descargada.")
            else:
                print("❌ No se pudo generar la imagen.")
    finally:
        client.close()
