from django.contrib import admin
from .models import Commande, Categorie, Plat, Panier, PanierItem, Category, Tag, Article, Commentaire, Like

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'utilisateur', 'statut', 'delivery_method', 'payment_method', 'total', 'date')
    list_filter = ('statut', 'delivery_method', 'payment_method')
    list_editable = ('statut', 'delivery_method', 'payment_method')
    search_fields = ('utilisateur__username',)

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    search_fields = ('nom',)

@admin.register(Plat)
class PlatAdmin(admin.ModelAdmin):
    list_display = ('nom', 'categorie', 'prix', 'disponibilite')
    list_filter = ('categorie', 'disponibilite')
    search_fields = ('nom',)

@admin.register(Panier)
class PanierAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'statut', 'date_creation')
    list_filter = ('statut',)
    search_fields = ('utilisateur__username',)

@admin.register(PanierItem)
class PanierItemAdmin(admin.ModelAdmin):
    list_display = ('panier', 'plat', 'quantite')
    search_fields = ('plat__nom',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'created_at')
    list_filter = ('status', 'category', 'author')
    list_editable = ('status', 'category')  # Éditer status directement
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'content', 'image')
        }),
        ('Métadonnées', {
            'fields': ('author', 'category', 'tags', 'status')
        }),
    )
    actions = ['publish_articles', 'unpublish_articles']

    def publish_articles(self, request, queryset):
        updated = queryset.update(status='published')
        self.message_user(request, f"{updated} article(s) publié(s) avec succès.")
    publish_articles.short_description = "Publier les articles sélectionnés"

    def unpublish_articles(self, request, queryset):
        updated = queryset.update(status='draft')
        self.message_user(request, f"{updated} article(s) passé(s) en brouillon.")
    unpublish_articles.short_description = "Passer les articles en brouillon"

@admin.register(Commentaire)
class CommentaireAdmin(admin.ModelAdmin):
    list_display = ('article', 'author', 'created_at')
    search_fields = ('content', 'author__username')

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('article', 'user', 'created_at')
    search_fields = ('user__username',)