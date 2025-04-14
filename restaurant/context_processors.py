# restaurant/context_processors.py
from .models import Panier, PanierItem

def cart_context(request):
    if request.user.is_authenticated:
        panier = Panier.objects.filter(utilisateur=request.user, statut='actif').first()
        if panier:
            cart_item_count = PanierItem.objects.filter(panier=panier).count()
        else:
            cart_item_count = 0
    else:
        cart_item_count = 0
    return {'cart_item_count': cart_item_count}