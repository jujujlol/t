import requests
import time
import json

def get_radio_metadata():
    url = "https://metadata-api.mytuner.mobi/api/v1/metadata-api/web/metadata?app_codename=mytuner_website&radio_id=396269&time=1730257815208"
    headers = {
        "Authorization": "HMAC mytuner_website:3GBw3zXz30yuwpp0C6OKkzgBI0jQtIb9gJCKEamoNqM"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)  # A?adido timeout de 10 segundos
        if response.status_code == 200:
            data = response.json()
            # Verificar que tenemos todos los datos necesarios
            if (data and 'radio_metadata' in data 
                and 'metadata' in data['radio_metadata'] 
                and data['radio_metadata']['metadata'] 
                and len(data['radio_metadata']['metadata'].strip()) > 0):
                return data
    except requests.RequestException as e:
        print(f"Error en la solicitud: {e}")
    return None

def send_discord_webhook(webhook_url, song_info):
    try:
        metadata = song_info['radio_metadata']
        song_data = metadata['metadata'].strip()
        
        # Verificar que tenemos una canci¨®n v¨¢lida
        if not song_data:
            print("Datos de cancion vacios, no se enviara notificacion")
            return False
            
        image_url = metadata.get('artwork_url_large', '')
        
        embed = {
            "title": "Nueva Cancion",
            "description": song_data,
            "color": 3447003
        }
        
        # Solo a?adir la imagen si existe
        if image_url:
            embed["thumbnail"] = {"url": image_url}
        
        payload = {
            "embeds": [embed]
        }
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        return response.status_code == 204
    except Exception as e:
        print(f"Error al enviar a Discord: {e}")
        return False

def main():
    webhook_url = "https://discord.com/api/webhooks/1301022519750430730/R9Vk_oavfAktsrHa_XAf16jlUghlQ_uU7-s2CZfCj8OoPeSMZ50s1Es1WMPq38qQTSIn"
    last_song = None
    error_count = 0
    
    print("Iniciando monitoreo...")
    
    while True:
        try:
            current_data = get_radio_metadata()
            
            if current_data:
                current_song = current_data['radio_metadata']['metadata'].strip()
                
                # Solo procesar si tenemos una canci¨®n v¨¢lida y es diferente a la anterior
                if current_song and current_song != last_song:
                    print("Nueva cancion detectada:", current_song)
                    success = send_discord_webhook(webhook_url, current_data)
                    if success:
                        print("Notificacion enviada a Discord")
                        last_song = current_song
                        error_count = 0  # Resetear contador de errores
                    else:
                        print("Error al enviar notificacion")
                        error_count += 1
            else:
                print("No se obtuvieron datos validos de la API")
                error_count += 1
            
            # Si hay muchos errores consecutivos, esperar m¨¢s tiempo
            if error_count > 5:
                print("Demasiados errores, esperando 2 minutos...")
                time.sleep(120)
                error_count = 0
            else:
                time.sleep(30)
            
        except Exception as e:
            print("Error general:", e)
            time.sleep(30)

if __name__ == "__main__":
    main()