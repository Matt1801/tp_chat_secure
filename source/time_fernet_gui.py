from fernet_gui import *
import time

from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken

TTL = 30

# TTL
class TimeFernetGUI(FernetGUI):
    # Dérivé la classe FernetGUI en TimeFernetGUI et utiliser les fonctions encrypt_at_time et decrypt_at_time dans les fonctions encrypt et decrypt, respectivement. Utilisez un TTL de 30 secondes et capturez l'exception potentielle (try/except InvalidToken as e) avec un log d'erreur en cas d'exception. Pour le temps, on utilisera int(time.time())
    
    def encrypt(self, message) -> bytes:
        """
        Args:
            message: message to encrypt

        Returns:
            encrypted message 
        """
        encrypted= Fernet(self.key)
        # Récupération du temps converti en int
        temps = int(time.time())
        # Chiffrage du message
        encrypted_message = encrypted.encrypt_at_time(bytes(message, 'utf-8'), temps)
        return encrypted_message

    def decrypt(self, message) -> str :
        """
        Args:
            message: message to decrypt

        Returns:
            decrypted message
        """
        message = base64.b64decode(message['data']) 
        decrypted= Fernet(self.key) 
        temps = int(time.time())
        try:
            decrypted_message = decrypted.decrypt_at_time(message, TTL, temps).decode('utf8')
            return decrypted_message
        except InvalidToken:
            self._log.info("TTL_ERROR: Expired message")
            return "Erreur_TTL"
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    # instanciate the class, create context and related stuff, run the main loop
    client = TimeFernetGUI()
    client.create()
    client.loop()