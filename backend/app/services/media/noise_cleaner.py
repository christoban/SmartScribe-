import numpy as np
import soundfile as sf
import noisereduce as nr
import asyncio
from pathlib import Path
from app.core.logger import get_logger
from app.utils.exceptions import AIProcessingException

logger = get_logger("NoiseCleaner")

class NoiseCleaner:
    TARGET_SR = 16000
    # On traite par blocs de 30 secondes pour ne pas saturer la RAM
    BLOCK_SIZE = TARGET_SR * 30 

    @classmethod
    async def clean_audio(cls, input_path: str, output_path: str = None) -> str:
        input_path = Path(input_path)
        if not output_path:
            output_path = input_path.with_name(f"{input_path.stem}_clean.wav")
        
        try:
            logger.info(f"✨ Nettoyage Pro (Streaming) : {input_path.name}")
            
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                None, cls._process_streaming_cleaning, str(input_path), str(output_path)
            )
            
            return str(output_path)
        except Exception as e:
            logger.error(f"❌ Erreur de nettoyage : {str(e)}")
            raise AIProcessingException(detail="Erreur lors du traitement du flux audio.")

    @classmethod
    def _process_streaming_cleaning(cls, input_path: str, output_path: str):
        """
        Nettoie l'audio bloc par bloc avec indexation pour l'apprentissage.
        """
        with sf.SoundFile(input_path) as infile:
            sr = infile.samplerate
            # 1. Apprendre le bruit sur le tout début (0.5s)
            noise_sample = infile.read(int(0.5 * sr))
            infile.seek(0)
            
            with sf.SoundFile(output_path, mode='w', samplerate=cls.TARGET_SR, 
                            channels=1, subtype='PCM_16') as outfile:
                
                # 2. Utiliser enumerate pour avoir l'index 'i'
                for i, block in enumerate(infile.blocks(blocksize=cls.BLOCK_SIZE, fill_value=0)):
                    if len(block.shape) > 1:
                        block = np.mean(block, axis=1)

                    # 3. Réduction de bruit
                    # On utilise le noise_sample seulement pour le premier bloc ou 
                    # on laisse noisereduce gérer l'estimation sur chaque bloc
                    reduced = nr.reduce_noise(
                        y=block,
                        sr=cls.TARGET_SR,
                        y_noise=noise_sample if i == 0 else None, 
                        prop_decrease=0.85,
                        stationary=False
                    )

                    peak = np.max(np.abs(reduced))
                    if peak > 0:
                        reduced = reduced / peak * 0.90
                    
                    outfile.write(reduced)
                    
        logger.info(f"✅ Nettoyage terminé (Streamed) -> {output_path}")