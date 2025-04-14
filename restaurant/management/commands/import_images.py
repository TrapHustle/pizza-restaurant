from django.core.management.base import BaseCommand
from django.core.files import File
import os
from restaurant.models import Plat, Categorie

class Command(BaseCommand):
    help = 'Importe les images depuis static/images/ vers le champ ImageField des plats'

    def handle(self, *args, **kwargs):
        static_images_path = 'C:/Users/kotch/MOVELIKEAPYTHON/restaurant_project/static/images/'

        # Dictionnaire pour associer les plats aux images (basé sur nom ou id)
        image_mapping = {
            # Pizzas
            'Margherita': 'pizza-1.jpg',
            'Hawaiian Pizza': 'pizza-2.jpg',
            'Bacon Crispy Thins': 'pizza-3.jpg',
            'Hawaiian Special': 'pizza-4.jpg',
            'Ultimate Overload': 'pizza-5.jpg',
            'Bacon Pizza': 'pizza-6.jpg',
            'Ham & Pineapple': 'pizza-7.jpg',
            # Burgers
            'Burger Classic': 'burger-1.jpg',
            'Cheeseburger': 'burger-2.jpg',
            'BBQ Burger': 'burger-3.jpg',
            # Boissons
            'Lemonade Juice': 'drink-1.jpg',
            'Pineapple Juice': 'drink-2.jpg',
            'Soda Drinks': 'drink-3.jpg',
            # Pâtes
            'Spaghetti Carbonara': 'pasta-1.jpg',
            'Penne Arrabbiata': 'pasta-2.jpg',
            'Lasagne Bolognese': 'pasta-3.jpg',
        }

        for plat in Plat.objects.all():
            # Vérifier si une image est déjà associée
            if plat.image:
                self.stdout.write(self.style.NOTICE(f'Image déjà existante pour {plat.nom}'))
                continue

            # Obtenir le nom de l'image depuis le dictionnaire
            image_name = image_mapping.get(plat.nom)

            # Si pas de correspondance dans le dictionnaire, essayer une logique générique
            if not image_name:
                # Déterminer le préfixe en fonction de la catégorie
                categorie_nom = plat.categorie.nom.lower()
                if 'pizza' in categorie_nom:
                    image_name = f'pizza-{plat.id}.jpg'
                elif 'burger' in categorie_nom:
                    image_name = f'burger-{plat.id}.jpg'
                elif 'boisson' in categorie_nom or 'drink' in categorie_nom:
                    image_name = f'drink-{plat.id}.jpg'
                elif 'pasta' in categorie_nom or 'pâtes' in categorie_nom:
                    image_name = f'pasta-{plat.id}.jpg'
                else:
                    image_name = None

            if image_name:
                image_path = os.path.join(static_images_path, image_name)
                if os.path.exists(image_path):
                    with open(image_path, 'rb') as f:
                        plat.image.save(image_name, File(f), save=True)
                    self.stdout.write(self.style.SUCCESS(f'Image importée pour {plat.nom}: {image_name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Image non trouvée pour {plat.nom}: {image_path}'))
            else:
                self.stdout.write(self.style.WARNING(f'Aucune image définie pour {plat.nom}'))