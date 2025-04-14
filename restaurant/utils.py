from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def envoyer_email(sujet, message, destinataires):
    """
    Fonction pour envoyer un email via Gmail SMTP.
    
    Args:
        sujet (str): Le sujet de l'email
        message (str): Le contenu du message
        destinataires (list): Liste des adresses email des destinataires
    
    Returns:
        bool: True si l'email a été envoyé avec succès, False sinon
    """
    if not destinataires or not isinstance(destinataires, list):
        logger.error("Liste de destinataires invalide ou vide")
        return False

    try:
        send_mail(
            sujet,
            message,
            settings.DEFAULT_FROM_EMAIL,
            destinataires,
            fail_silently=False,
        )
        logger.info(f"Email envoyé avec succès à {destinataires}")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email à {destinataires}: {str(e)}")
        return False