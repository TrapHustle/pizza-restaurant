from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.contrib.auth.models import User

class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.nom

class Plat(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField()
    prix = models.DecimalField(max_digits=6, decimal_places=2)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='plats/', blank=True, null=True)
    disponibilite = models.BooleanField(default=True)

    def __str__(self):
        return self.nom

    @property
    def image_full_url(self):
        if self.image:
            return self.image.url
        return '/static/images/default.jpg'

class Panier(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    statut = models.CharField(
        max_length=20,
        choices=[
            ('actif', 'Actif'),
            ('validé', 'Validé'),
            ('termine', 'Terminé'),
        ],
        default='actif'
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Panier de {self.utilisateur} - {self.statut}"

class PanierItem(models.Model):
    panier = models.ForeignKey(Panier, on_delete=models.CASCADE, related_name='items')
    plat = models.ForeignKey(Plat, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantite} x {self.plat.nom} dans {self.panier}"

class Commande(models.Model):
    STATUS_CHOICES = (
        ('preparation', 'Préparation'),
        ('livreur', 'Livreur'),
        ('prete', 'Commande Prête'),
    )
    DELIVERY_CHOICES = (
        ('livraison', 'Livraison à domicile'),
        ('emporter', 'À emporter'),
    )
    PAYMENT_CHOICES = (
        ('wave', 'Wave'),
        ('orange_money', 'Orange Money'),
    )
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='preparation')
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default='emporter')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='wave')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commande #{self.id} de {self.utilisateur} - {self.get_statut_display()}"

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Article(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Brouillon'),
        ('pending', 'En attente de validation'),
        ('published', 'Publié'),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to='articles/', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-published_at', '-created_at']

class Commentaire(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commentaire de {self.author} sur {self.article}"

class Like(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('article', 'user')

    def __str__(self):
        return f"{self.user} a aimé {self.article}"