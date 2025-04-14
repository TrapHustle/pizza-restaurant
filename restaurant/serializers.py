from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Article, Like, Plat, Panier, PanierItem, Commande, Category, Tag, Categorie
from restaurant import models

# Serializer pour Categorie (utilisé dans Plat)
class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = ['id', 'nom', 'description']

from .models import Commentaire
class CommentaireSerializer(serializers.ModelSerializer):  # Correct: A serializer
    class Meta:
        model = Commentaire
        fields = ['id', 'article', 'author', 'content', 'created_at']


    def __str__(self):
        return f"Commentaire de {self.author} sur {self.article}"

# Serializer pour Category (utilisé dans Article)
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

# Serializer pour Tag (utilisé dans Article)
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']

# Serializer pour User (utilisé dans Panier, Commande, et Article)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

# Serializer pour Plat (utilisé dans PanierItem)
class PlatSerializer(serializers.ModelSerializer):
    categorie = CategorieSerializer(read_only=True)

    class Meta:
        model = Plat
        fields = ['id', 'nom', 'categorie', 'prix', 'disponibilite']

# Serializer pour PanierItem (utilisé dans Panier)
class PanierItemSerializer(serializers.ModelSerializer):
    plat = PlatSerializer(read_only=True)
    plat_id = serializers.PrimaryKeyRelatedField(queryset=Plat.objects.all(), source='plat', write_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = PanierItem
        fields = ['id', 'plat', 'plat_id', 'quantite', 'subtotal']

    def get_subtotal(self, obj):
        return obj.quantite * obj.plat.prix

# Serializer pour Panier
class PanierSerializer(serializers.ModelSerializer):
    utilisateur = UserSerializer(read_only=True)
    items = PanierItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Panier
        fields = ['id', 'utilisateur', 'statut', 'date_creation', 'items', 'total']
        read_only_fields = ['utilisateur', 'date_creation']

    def get_total(self, obj):
        return sum(item.quantite * item.plat.prix for item in obj.items.all())

    def create(self, validated_data):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Utilisateur non authentifié.")
        return Panier.objects.create(utilisateur=request.user, **validated_data)

# Serializer pour Commande
class CommandeSerializer(serializers.ModelSerializer):
    utilisateur = UserSerializer(read_only=True)
    items = serializers.SerializerMethodField()

    class Meta:
        model = Commande
        fields = ['id', 'utilisateur', 'statut', 'delivery_method', 'payment_method', 'total', 'date', 'items']
        read_only_fields = ['utilisateur', 'total', 'date', 'items']

    def get_items(self, obj):
        panier = Panier.objects.filter(utilisateur=obj.utilisateur, statut='termine').last()
        if panier:
            return PanierItemSerializer(panier.items.all(), many=True).data
        return []

    def validate(self, data):
        request = self.context.get('request')
        panier = Panier.objects.filter(utilisateur=request.user, statut='actif').first()
        if not panier or not panier.items.exists():
            raise serializers.ValidationError("Le panier est vide.")
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        panier = Panier.objects.filter(utilisateur=request.user, statut='actif').first()
        total = sum(item.quantite * item.plat.prix for item in panier.items.all())
        commande = Commande.objects.create(
            utilisateur=request.user,
            total=total,
            **validated_data
        )
        panier.statut = 'termine'
        panier.save()
        return commande

# Serializer pour Article
class ArticleSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'author', 'category', 'tags', 'status', 'created_at', 'published_at']

    
class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    article = serializers.PrimaryKeyRelatedField(queryset=Article.objects.all())

    class Meta:
        model = Like
        fields = ['id', 'article', 'user', 'created_at']
        read_only_fields = ['user', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Utilisateur non authentifié.")
        validated_data['user'] = request.user
        return super().create(validated_data)