import httpx
import asyncio
import time
from app.core import constants

API_URL = "http://localhost:8000/api/v1/media"
# Remplace par un vrai chemin de fichier sur ton PC pour le test
TEST_FILE = "votre_video_test.mp4" 

async def test_full_pipeline():
    async with httpx.AsyncClient(timeout=60.0) as client:
        # 1. Vérification de l'API
        print("🔍 Vérification du serveur...")
        try:
            health = await client.get("http://localhost:8000/health")
            print(f"Status: {health.json()['status']}")
        except Exception:
            print("❌ Erreur: Le serveur FastAPI n'est pas lancé !")
            return

        # 2. Upload du média
        print(f"📤 Upload de {TEST_FILE}...")
        with open(TEST_FILE, "rb") as f:
            files = {"file": (TEST_FILE, f, "video/mp4")}
            # Note: Ajoute tes headers d'auth si get_current_user est activé
            response = await client.post(f"{API_URL}/upload", files=files)
        
        if response.status_code != 200:
            print(f"❌ Erreur Upload: {response.text}")
            return
        
        media_data = response.json()
        media_id = media_data["id"]
        print(f"✅ Fichier accepté ! ID: {media_id}")

        # 3. Surveillance du traitement (Polling)
        print("⏳ Traitement en cours (Audio + Vision)...")
        start_time = time.time()
        
        while True:
            # On simule la récupération du statut
            # (Tu pourras créer un endpoint GET /media/{id} pour ça)
            res = await client.get(f"{API_URL}/{media_id}")
            status = res.json().get("status")
            
            elapsed = int(time.time() - start_time)
            print(f"⏱️ {elapsed}s - Statut actuel : {status}")

            if status == constants.STATUS_COMPLETED:
                print("\n🎉 SUCCÈS ! La note est prête.")
                print("-" * 30)
                print(res.json().get("text")) # Ta note Llama-3.3
                print("-" * 30)
                break
            elif status == constants.STATUS_FAILED:
                print("\n❌ Le pipeline a échoué. Vérifie les logs du Worker.")
                break
            
            await asyncio.sleep(5) # Attend 5s avant de redemander

if __name__ == "__main__":
    asyncio.run(test_full_pipeline())