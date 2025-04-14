from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from . import views
from django.contrib.auth import views as auth_views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.authtoken.views import obtain_auth_token

# Router pour l'API REST
router = DefaultRouter()
router.register(r'plats', views.PlatViewSet)
router.register(r'articles', views.ArticleViewSet)
router.register(r'panier', views.PanierViewSet)
router.register(r'commandes', views.CommandeViewSet)
router.register(r'categories', views.CategorieViewSet)  # For Categorie (used by Plat)
router.register(r'article-categories', views.CategoryViewSet)  # For Category (used by Article)



router.register(r'panier-items', views.PanierItemViewSet)
router.register(r'tags', views.TagViewSet)
router.register(r'commentaires', views.CommentaireViewSet)
router.register(r'likes', views.LikeViewSet)

# Configuration Swagger/ReDoc
schema_view = get_schema_view(
    openapi.Info(
        title="Restaurant API",
        default_version='v1',
        description="API pour le restaurant en ligne",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@restaurant.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# URLs mappées
urlpatterns = [
    # index.html -> Page d'accueil (liste des plats)
    path('', views.PlatListView.as_view(), name='index'),
    
    # menu.html -> Liste des plats
    path('menu/', views.MenuListView.as_view(), name='menu'),
    path('menu/<str:categorie_nom>/', views.MenuListView.as_view(), name='menu_by_category'),
    
    # plat/<id>/ -> Détails d'un plat
    path('plat/<int:pk>/', views.PlatDetailView.as_view(), name='plat_detail'),
    
    # Panier
    path('panier/', views.voir_panier, name='voir_panier'),
    path('ajouter_au_panier/<int:plat_id>/', views.ajouter_au_panier, name='ajouter_au_panier'),
    path('rechercher/', views.rechercher_plats, name='rechercher_plats'),
    path('modifier_quantite/<int:item_id>/<str:action>/', views.modifier_quantite, name='modifier_quantite'),
    path('supprimer_du_panier/<int:item_id>/', views.supprimer_du_panier, name='supprimer_du_panier'),
    path('passer_commande/', views.passer_commande, name='passer_commande'),
    
    # blog.html -> Liste des articles
    path('blog/', views.ArticleListView.as_view(), name='blog'),
    
    # blog-single.html -> Détails d'un article
    path('blog-single/<int:pk>/', views.ArticleDetailView.as_view(), name='blog_single'),
    
    # Commentaire
    path('blog-single/<int:article_id>/commentaire/', views.add_comment, name='ajouter_commentaire'),
    
    # contact.html -> Page "À propos"
    path('contact/', TemplateView.as_view(template_name='restaurant/contact.html'), name='contact'),
    
    # service.html -> Page "Confidentialité"
    path('service/', TemplateView.as_view(template_name='restaurant/service.html'), name='service'),
    
    # API REST
    path('api/', include(router.urls)),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    

     

    path('commande-confirmee/', views.commande_confirmee, name='commande_confirmee'),
    path('suivi-commande/<int:commande_id>/', views.suivi_commande, name='suivi_commande'),
    path('suivi-commandes/', views.suivi_commandes, name='suivi_commandes'),
    path('plat/<int:plat_id>/', views.detail_plat, name='detail_plat'),
    path('plat/<int:plat_id>/', views.PlatDetailView.as_view(), name='detail_plat'),
    
    # Swagger et ReDoc
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('article/<int:pk>/edit/', views.ArticleEditView.as_view(), name='article_edit'),
    path('article/<int:pk>/delete/', views.ArticleDeleteView.as_view(), name='article_delete'),
    
    # Authentification
    path('login/', auth_views.LoginView.as_view(template_name='restaurant/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('register/', views.register, name='register'),
    path('password_reset/', views.custom_password_reset, name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='restaurant/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='restaurant/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='restaurant/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    path('article/create/', views.ArticleCreateView.as_view(), name='article_create'),
    path('article/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('article/<int:pk>/like/', views.like_article, name='like_article'),
    path('admin/pending-articles/', views.PendingArticleListView.as_view(), name='pending_articles'),
    path('admin/publish-article/<int:pk>/', views.publish_article, name='publish_article'),
]