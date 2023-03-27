from ciphered_gui import *
import hashlib

from cryptography.fernet import Fernet

# Authenticated Symetric Encryption
class FernetGUI(CipheredGUI):
    # Dérivé la classe CipheredGUI pour créer FernetGUI. La seule modification portera sur la fonction encrypt/decrypt, ainsi que run_chat qui utilisera sha256().digest() + base64.b64encode() au lieu de PBKDF2HMAC
    
    # redéfinition de la fonction run_chat
    def run_chat(self, sender, app_data) -> None :

        # On reprend la méthode de la classe parente
        host = dpg.get_value("connection_host")
        port = int(dpg.get_value("connection_port"))
        name = dpg.get_value("connection_name")
        password = dpg.get_value("connection_pswd")
        self._log.info(f"Connecting {name}@{host}:{port}")

        self._callback = GenericCallback()

        self._client = ChatClient(host, port)
        self._client.start(self._callback)
        self._client.register(name)

        dpg.hide_item("connection_windows")
        dpg.show_item("chat_windows")
        dpg.set_value("screen", "Connecting")

        password = dpg.get_value("connection_pswd")

        # Génération de la clé de chiffrement
        self.key = base64.b64encode(hashlib.sha256(password.encode()).digest())
        
    # Redéfinition de la classe encrypt
    def encrypt(self, message) -> bytes:
        """
        Args:
            message: message to encrypt

        Returns:
            encrypted message 
        """
        # Conversion du message en bytes
        message_bytes = bytes(message, 'utf-8') 
        # Chiffrage du message
        encrypted_message = Fernet(self.key).encrypt(message_bytes)
        return encrypted_message
    
    # Redéfinition de la classe decrypt
    def decrypt(self, message) -> str :
        """
        Args:
            message: message to decrypt

        Returns:
            decrypted message
        """
        message = base64.b64decode(message['data']) 
        decrypted_message = Fernet(self.key).decrypt(message).decode('utf8')
        return decrypted_message
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    # instanciate the class, create context and related stuff, run the main loop
    client = FernetGUI()
    client.create()
    client.loop()