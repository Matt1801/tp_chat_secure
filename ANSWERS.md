# TP Secure chat
Date butoir de rendu : 27 mars 2023 00h00
## Prise en main
**1) Comment s'appelle cette topology ?**
La topologie du chat semble être sous forme d'étoile. En effet, à chaque envoie de message par un client le serveur le récupère et le renvoie vers les autres clients connectés au serveur.
**2) Que remarquez vous dans les logs ?** 
Chaque message envoyé par le client est d'abord reçu par le serveur puis renvoyé vers les autres clients.
**3) Pourquoi est-ce un problème et quel principe cela viole t-il ?**
- Confidentialité : le messages est envoyé à tous les utilisateurs à chaque fois et le serveur à accès aux messages en clair.
- Disponibilité : le serveur représente un unique point de défaillance en effet si ce dernier ne fonctionne plus les communications sont impossibles.

**4) Quelle solution la plus *simple* pouvez-vous mettre en place pour éviter cela ? Détaillez votre réponse.**
Pour palier le problème de confidentialité on peut utiliser un chiffrage des messages avant l'envoie ainsi qu'un déchiffrage au moment de la réception.

## Chiffrement
**1) Est ce que urandom est un bon choix pour de la cryptographie ? Pourquoi ?**
Tout d'abord la fonction os.urandom() a été crée spécialement pour la cryptographie. En effet, c'est un bon choix pour la cryptographie d'une petite application car se basant sur l'entropie il génère un nombre aléatoire plus intéressant que la fonction random(). Cependant, dans un application plus importante et à risque il peut être nécessaire d'utiliser un générateur plus complexe.

**2) Pourquoi utiliser ses primitives cryptographiques peut être dangereux ?**
Utiliser ses primitives cryptographique peut représenter un danger car elles doivent être utiliser correctement. En effet, une erreur d'implémentation provoquera une vulnérabilité dans le système. L'utilisation de bibliothèque pré-conçu permet de limiter ces problèmes d'implémentation.

**3) Pourquoi malgré le chiffrement un serveur malveillant peut il nous nuire encore ?**
Le chiffrement permet une protection des données par rapport aux utilisateurs cependant un serveur malveillant pourrait modifier ou enregistrer les données pour un usage malveillant.

**4) Quelle propriété manque t-il ici ?**
La propriété manquante est l'intégrité. En effet, le message pourrait être modifié entre les différents utilisateurs durant le transfert par le serveur. En utilisant une authentification du message on pourrait ainsi assurer son intégrité.

## Authenticated Symetric Encryption
**1) Pourquoi Fernet est moins risqué que le précédent chapitre en terme d'implémentation ?**
Comment explicité précédemment il est nécessaire d'ajouter une authentification des messages. HMAC qui est utilisé par le module Fernet permet celà. Avec cette authentification l'intégrité est conservé.

**2) Un serveur malveillant peut néanmoins attaqué avec des faux messages, déjà utilisé dans le passé. Comment appel t-on cette attaque ?**
Ce type d'attaque se nomme l'attaque par rejeu. Cette dernière est une forme d'attaque qui utilise les messages précédemment envoyé. Avec cette méthode il contourne l'identification en réutilisant ce message déjà reçu.

**3) Quelle méthode simple permet de s'en affranchir ?**
Une méthode simple permettant de s'en affranchir serai d'ajouter une durée de vie au message. En effet en donnant un identifiant unique à chaque message leur authentification sera conservé.

## TTL (Time To Live)
**1) Remarquez vous une différence avec le chapitre précédent ?**
En ajoutant une validité au message et que nous renvoyons ce dernier une erreur est transmise sur les logs du serveur.

**2) Maintenant soustrayez 45 au temps lors de l'émission. Que se passe t-il et pourquoi ?**
Le message étant déjà hors de sa temporalité de validité (30-45=un nombre négatif) nous observons immédiatement l'erreur.

**3) Est-ce efficace pour se protéger de l'attaque du précédent chapitre ?** 
Cette méthode est efficace et peut être améliorer en diminuant le time to live ce qui augmentera la fiabilité.

**4) Quelle(s) limite(s) cette solution peut rencontrer dans la pratique ?**
Cette implémentation peut être limité par la perception temporel du serveur en effet en cas de ralentissement du réseau le TTL pourra devenir plus long ou ne pas fonctionné correctement. Nous pouvons donc perdre non pas seulement l'intégrité mais également le message en lui même. De plus, en se basant sur une horloge oblige cette dernière à être commune à tout les utilisateurs.

## Regard critique
**J'ai pris des raccourcis, pris des décisions arbitraires et utilisé des bibliothèques tiers. Ai-je laissé des vulnérabilités ?**
- Tout d'abord le premier problème est l'affichage des mots de passe. En effet ces derniers ne sont pas cachés lors de leur renseignement il serait donc nécessaire d'utiliser un champ plus discret.
- Nous pouvons également jugé risqué le fait d'utiliser une librairie extérieur il est nécessaire de se renseigner sur cette dernière au niveau du code lui même pour s'assurer de la fiabilité et de la confidentialité des solutions proposées.
- De plus le time to live laisse tout de même une marge aux attaques par rejeu qui pourrait être utiliser en plus d'un DDOS qui ralentirait le serveur.
- Il est également important de noter que le contenu des messages n'est pas filtré ce qui peut provoquer un danger pour les utilisateurs face aux contenus malveillants qui pourrait leur être envoyés.
- Il y a également un problème en cas de création de deux utilisateurs aux noms similaires le serveur est alors surchargé au niveau des données envoyées à chaque message.
