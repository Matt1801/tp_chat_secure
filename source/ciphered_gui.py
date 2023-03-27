import os
import base64
from basic_gui import *

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import padding

TAILLE_BLOCK = 128
TAILLE_OCTET = 16
ITERATIONS = 100000
salt = b"IsOkSaltTier"

# Chiffrement
class CipheredGUI(BasicGUI):
    def __init__(self) -> None:
        # Surcharger le constructeur pour y inclure le champ self._key qui contiendra la clef de chiffrement (default : None)
        super().__init__()
        self.key = None
        
    # Surcharger la fonction _create_connection_window() pour y inclure un champ password 
    def _create_connection_window(self) -> None:
        # windows about connexion
        with dpg.window(label="Connection", pos=(200, 150), width=400, height=300, show=False, tag="connection_windows"):

            for field in ["host", "port", "name", "pswd"]:
                with dpg.group(horizontal=True):
                    dpg.add_text(field)
                    dpg.add_input_text(
                        default_value=DEFAULT_VALUES[field], tag=f"connection_{field}")
            dpg.add_button(label="Connect", callback=self.run_chat)

    # Surcharger la fonction run_chat() pour y inclure la récupération du mot de passe et faire la dérivation de la clef (self.key)
    def run_chat(self, sender, app_data) -> None:
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

        self.key = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=TAILLE_OCTET,
            salt=salt,
            iterations=ITERATIONS,
            backend=default_backend()
        ).derive(bytes(password, "utf8"))
        
    # Créer une fonction encrypt(), prenant une string et retournant un tuple de bytes (iv, encrypted)
    def encrypt(self, message):
        """
        Args:
            message: message to encrypt

        Returns:
            tuple: (iv, encrypted_message) 
        """
        # Génération aléatoire d'un vecteur d'initialisation
        iv = os.urandom(TAILLE_OCTET)
        
        encryptor = Cipher(
            algorithms.AES(self.key),
            modes.CTR(iv),
            backend=default_backend()
        ).encryptor()
        
        padder = padding.PKCS7(TAILLE_BLOCK).padder()
        padded_data = padder.update(bytes(message,"utf8")) + padder.finalize()
        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        return iv, encrypted
    

    # Créer une fonction decrypt(), prenant un tuple en paramètre et retournant une string utf8
    def decrypt(self, message):
        """
        Decryption of the message with pkcs7

        Args:
            message: message to decrypt

        Returns:
            message: decrypted message
        """
        iv = base64.b64decode(message[0]['data'])
        message = base64.b64decode(message[1]['data'])
        decryptor = Cipher(
            algorithms.AES(self.key),
            modes.CTR(iv),
            backend=default_backend()
        ).decryptor()
        
        decrypted_data = decryptor.update(message) + decryptor.finalize()
        unpadder = padding.PKCS7(TAILLE_BLOCK).unpadder()
        unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
        return unpadded_data.decode("utf-8")

    def send(self, text) -> None:
        """
        Encryption of a message, then send it
        Args:
            text (string): message to send
        """
        # Chiffrer le message
        message = self.encrypt(text)
        # Envoie du message chiffré
        self._client.send_message(message)

    def recv(self) -> None:
        """
        Receive message and decryption
        """
        if self._callback is not None:
            for user, message in self._callback.get():
                # Déchiffrage
                message = self.decrypt(message)
                # Affichage du message
                self.update_text_screen(f"{user} : {message}")
            self._callback.clear()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    # instanciate the class, create context and related stuff, run the main loop
    client = CipheredGUI()
    client.create()
    client.loop()