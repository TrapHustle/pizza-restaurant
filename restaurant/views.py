# restaurant/views.py
from datetime import datetime, timezone
from venv import logger
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models import Sum, F
from rest_framework.decorators import action

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings
from django.core.mail import send_mail
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.utils import timezone
from .models import Category, Panier, Commande
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from rest_framework import viewsets

from django.shortcuts import render, redirect
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from .utils import envoyer_email
from .forms import CustomUserCreationForm



from restaurant.utils import envoyer_email

from .forms import ArticleForm, CommentForm
from .models import Categorie, Like, Plat, Panier, PanierItem, Tag
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from rest_framework.permissions import IsAuthenticated
from .models import Plat, Panier, PanierItem, Article, Commande, Commentaire  # Ajoute Commentaire ici
from .serializers import CategorieSerializer, CategorySerializer, CommandeSerializer, CommentaireSerializer, LikeSerializer, PanierItemSerializer, PanierSerializer, PlatSerializer, ArticleSerializer, TagSerializer
from restaurant import serializers


# Vues E-commerce
class PlatListView(ListView):
    model = Plat
    template_name = 'restaurant/index.html'
    context_object_name = 'plats'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add a featured dish to the context
        context['featured_plat'] = Plat.objects.first()  # Or any logic to select a featured dish
        return context
    
class PlatDetailView(DetailView):
    model = Plat
    template_name = 'restaurant/detail.html'
    context_object_name = 'plat'
   

@login_required
def ajouter_au_panier(request, plat_id):
    plat = get_object_or_404(Plat, id=plat_id)
    # Récupérer ou créer un panier actif pour l'utilisateur
    panier, created = Panier.objects.get_or_create(
        utilisateur=request.user,
        statut='actif',
        defaults={'statut': 'actif'}
    )
    # Ajouter ou mettre à jour l'item dans le panier
    panier_item, created = PanierItem.objects.get_or_create(
        panier=panier,
        plat=plat,
        defaults={'quantite': 1}
    )
    if not created:
        panier_item.quantite += 1
        panier_item.save()

    # Envoyer un e-mail de confirmation
    subject = 'Confirmation d’ajout au panier'
    message = f'Vous avez ajouté {plat.nom} au panier.\nPrix : {plat.prix:.2f} FCFA.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [request.user.email]  # Utiliser l'e-mail de l'utilisateur connecté
    send_mail(subject, message, from_email, recipient_list, fail_silently=True)

    return redirect('menu')

@login_required
def voir_panier(request):
    panier = Panier.objects.filter(utilisateur=request.user, statut='actif').first()
    if request.method == 'POST':
        if panier and panier.panieritem_set.exists():
            return redirect('passer_commande')
    return render(request, 'restaurant/panier.html', {'panier': panier})

def rechercher_plats(request):
    query = request.GET.get('q')
    plats = Plat.objects.filter(Q(nom__icontains=query) | Q(description__icontains=query))
    return render(request, 'restaurant/plat_list.html', {'plats': plats})

# Vues Blog

# Liste des articles (page Blog)
class ArticleListView(ListView):
    model = Article
    template_name = 'restaurant/blog.html'
    context_object_name = 'articles'
    paginate_by = 6

    def get_queryset(self):
        # N'afficher que les articles publiés pour les utilisateurs normaux
        return Article.objects.filter(status='published')

# Détail d'un article (page Blog Single)
class ArticleDetailView(DetailView):
    model = Article
    template_name = 'restaurant/blog_single.html'
    context_object_name = 'article'

    def get_queryset(self):
        # N'afficher que les articles publiés
        return Article.objects.filter(status='published')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        context['user_has_liked'] = self.request.user.is_authenticated and self.object.likes.filter(user=self.request.user).exists()
        return context

# Créer un article (utilisateur connecté)
class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'restaurant/article_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.status = 'pending'  # Article en attente de validation
        messages.success(self.request, "Votre article a été soumis et est en attente de validation par l'administrateur.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog')

# Ajouter un commentaire (utilisateur connecté)
@login_required 
def add_comment(request, pk):
    article = get_object_or_404(Article, pk=pk, status='published')
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.author = request.user
            comment.save()
            messages.success(request, "Votre commentaire a été ajouté.")
            return redirect('blog_single', pk=article.pk)
    return redirect('blog_single', pk=article.pk)

# Liker un article (utilisateur connecté)
@login_required
def like_article(request, pk):
    article = get_object_or_404(Article, pk=pk, status='published')
    like, created = Like.objects.get_or_create(article=article, user=request.user)
    if not created:
        like.delete()  # Si l'utilisateur a déjà liké, cela supprime le like (toggle)
    return redirect('blog_single', pk=article.pk)

# Vue pour l'admin : Liste des articles en attente
class PendingArticleListView(UserPassesTestMixin, ListView):
    model = Article
    template_name = 'restaurant/admin_pending_articles.html'
    context_object_name = 'articles'

    def test_func(self):
        return self.request.user.is_superuser  # Seuls les superadmins peuvent accéder

    def get_queryset(self):
        return Article.objects.filter(status='pending')

# Vue pour l'admin : Publier un article
@login_required
def publish_article(request, pk):
    if not request.user.is_superuser:
        messages.error(request, "Vous n'avez pas la permission de publier des articles.")
        return redirect('blog')
    
    article = get_object_or_404(Article, pk=pk, status='pending')
    if request.method == 'POST':
        article.status = 'published'
        article.published_at = timezone.now()
        article.save()
        messages.success(request, f"L'article '{article.title}' a été publié avec succès.")
        return redirect('pending_articles')
    return render(request, 'restaurant/admin_confirm_publish.html', {'article': article})
# Vues API
class PlatViewSet(viewsets.ModelViewSet):
    queryset = Plat.objects.all()
    serializer_class = PlatSerializer
    permission_classes = [IsAuthenticated]

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]


class MenuListView(ListView):
    model = Plat
    template_name = 'restaurant/menu.html'
    context_object_name = 'plats'

    def get_queryset(self):
        categorie_nom = self.kwargs.get('categorie_nom', 'Pizza').capitalize()
        try:
            categorie = Categorie.objects.get(nom=categorie_nom)
            return Plat.objects.filter(categorie=categorie)
        except Categorie.DoesNotExist:
            return Plat.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Categorie.objects.all()
        context['current_categorie'] = self.kwargs.get('categorie_nom', 'Pizza').capitalize()
        return context 
    
def menu(request):
    plats = Plat.objects.filter(disponibilite=True)
    categories = Categorie.objects.all()
    context = {
        'plats': plats,
        'categories': categories,
        
        'bg_image_url': '/static/images/bg_1.jpg',  # Changé de bg-1.jpg à bg_1.jpg
    }
    return render(request, 'restaurant/menu.html', context)

@login_required
def voir_panier(request):
    panier = Panier.objects.filter(utilisateur=request.user, statut='actif').first()
    if request.method == 'POST':
        if panier and panier.panieritem_set.exists():
            total = sum(item.plat.prix * item.quantite for item in panier.panieritem_set.all())
            Commande.objects.create(utilisateur=request.user, total=total, statut='en_attente')
            panier.statut = 'validé'
            panier.save()
            return redirect('passer_commande')  # Rediriger vers la simulation de paiement
    return render(request, 'restaurant/panier.html', {'panier': panier})


@login_required
def modifier_quantite(request, item_id, action):
    panier_item = get_object_or_404(PanierItem, id=item_id, panier__utilisateur=request.user, panier__statut='actif')
    if action == 'augmenter':
        panier_item.quantite += 1
    elif action == 'diminuer' and panier_item.quantite > 1:
        panier_item.quantite -= 1
    panier_item.save()
    return redirect('voir_panier')

@login_required
def supprimer_du_panier(request, item_id):
    panier_item = get_object_or_404(PanierItem, id=item_id, panier__utilisateur=request.user, panier__statut='actif')
    panier_item.delete()
    return redirect('voir_panier')

# restaurant/views.py

@login_required  # Ensure user is logged in
def passer_commande(request):
    # Use 'utilisateur' instead of 'user' to match the model field
    panier = Panier.objects.filter(utilisateur=request.user).first()

    if not panier or not panier.panieritem_set.exists():
        messages.error(request, "Votre panier est vide.")
        return redirect('panier')

    # Get form data
    payment_method = request.POST.get('payment_method')
    otp = request.POST.get('otp', '')

    # Validate payment method
    if not payment_method:
        messages.error(request, "Veuillez sélectionner une méthode de paiement.")
        return redirect('panier')

    # Validate OTP for Orange Money
    if payment_method == 'orange_money' and otp != '123456':  # Simulate OTP check
        messages.error(request, "OTP invalide.")
        return redirect('panier')

    # Calculate total
    total = panier.panieritem_set.aggregate(
        total=Sum(F('plat__prix') * F('quantite'))
    )['total'] or 0

    # Create a new order
    commande = Commande.objects.create(
        utilisateur=request.user,  # Use 'utilisateur' instead of 'user'
        total=total,
        payment_method=payment_method,
        statut='en_attente',
        date_creation=datetime.now()
    )

    # Transfer cart items to order items
    for item in panier.panieritem_set.all():
        Commande.objects.create(
            commande=commande,
            plat=item.plat,
            quantite=item.quantite,
            prix=item.plat.prix
        )

    # Clear the cart
    panier.panieritem_set.all().delete()

    # Success message
    messages.success(request, "Votre commande a été passée avec succès !")

    # Redirect to confirmation page
    return redirect('commande_confirmee', commande_id=commande.id)

@login_required
def commande_confirmee(request, commande_id):
    # Use 'utilisateur' instead of 'user'
    commande = Commande.objects.get(id=commande_id, utilisateur=request.user)
    context = {
        'commande': commande,
        'message': 'Votre commande a été confirmée avec succès !'
    }
    return render(request, 'restaurant/commande_confirmee.html', context)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Inscription réussie ! Bienvenue sur Pizza Restaurant.")
            return redirect('index')
        else:
            messages.error(request, "Erreur lors de l'inscription. Veuillez vérifier les informations.")
            return render(request, 'restaurant/register.html', {'form': form})
    else:
        form = CustomUserCreationForm()
    return render(request, 'restaurant/register.html', {'form': form})

def custom_password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email__iexact=email.lower())
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            full_url = f"{request.scheme}://{request.get_host()}{reset_url}"
            sujet = 'Réinitialisation de votre mot de passe'
            message = (
                f"Bonjour {user.username},\n\n"
                f"Vous avez demandé à réinitialiser votre mot de passe pour {settings.SITE_NAME}.\n"
                f"Cliquez sur ce lien pour définir un nouveau mot de passe :\n\n"
                f"{full_url}\n\n"
                f"Ce lien est valide pendant 24 heures.\n"
                f"Si vous n'avez pas fait cette demande, ignorez cet e-mail.\n\n"
                f"Cordialement,\nL'équipe {settings.SITE_NAME}"
            )
            if envoyer_email(sujet, message, [email]):
                return render(request, 'restaurant/password_reset_done.html')
            else:
                return render(request, 'restaurant/password_reset.html', {
                    'error': "Erreur lors de l'envoi de l'e-mail. Veuillez réessayer."
                })
        except User.DoesNotExist:
            return render(request, 'restaurant/password_reset.html', {
                'error': "Cet e-mail n'est pas associé à un compte."
            })
    return render(request, 'restaurant/password_reset.html')

# ... (le reste du fichier reste inchangé : PlatListView, ajouter_au_panier, etc.)

class DashboardView(LoginRequiredMixin, ListView):
    model = Article
    template_name = 'restaurant/dashboard.html'
    context_object_name = 'articles'

    def get_queryset(self):
        # Ne montrer que les articles créés par l'utilisateur connecté
        return Article.objects.filter(author=self.request.user)

# Vue pour la liste des articles (blog)
class ArticleListView(ListView):
    model = Article
    template_name = 'restaurant/blog.html'
    context_object_name = 'articles'
    paginate_by = 6

    def get_queryset(self):
        queryset = Article.objects.filter(status='published')
        tag = self.request.GET.get('tag')
        if tag:
            queryset = queryset.filter(tags__slug=tag)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = Tag.objects.all()
        context['selected_tag'] = self.request.GET.get('tag')
        return context

# Vues pour modifier et supprimer un article
class ArticleEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'restaurant/article_form.html'
    success_url = reverse_lazy('dashboard')

    def test_func(self):
        article = self.get_object()
        return article.author == self.request.user

    def form_valid(self, form):
        messages.success(self.request, "L'article a été modifié avec succès !")
        return super().form_valid(form)
    
class ArticleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Article
    template_name = 'restaurant/article_confirm_delete.html'
    success_url = reverse_lazy('dashboard')

    def test_func(self):
        article = self.get_object()
        return article.author == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(request, "L'article a été supprimé avec succès !")
        return super().delete(request, *args, **kwargs)
    
@require_POST
@login_required
def commande_confirmee(request):
    # Get the user's cart
    panier = Panier.objects.filter(utilisateur=request.user, statut='actif').first()
    
    if not panier or not panier.panieritem_set.exists():
        messages.error(request, "Votre panier est vide.")
        return redirect('panier')

    # Get form data
    delivery_method = request.POST.get('delivery_method', 'emporter')
    payment_method = request.POST.get('payment_method', 'wave')

    # Calculate total
    total = panier.panieritem_set.aggregate(
        total=Sum(F('plat__prix') * F('quantite'))
    )['total'] or 0

    # Create Commande
    commande = Commande.objects.create(
        utilisateur=request.user,
        total=total,
        statut='preparation',
        delivery_method=delivery_method,
        payment_method=payment_method
    )

    # Clear the cart (optional, can be skipped if you want to keep items)
    panier.panieritem_set.all().delete()
    panier.statut = 'termine'
    panier.save()

    return render(request, 'restaurant/commande_confirmee.html', {
        'commande': commande
    })


@login_required
def suivi_commande(request, commande_id):
    try:
        commande = Commande.objects.get(id=commande_id, utilisateur=request.user)
    except Commande.DoesNotExist:
        messages.error(request, "Commande non trouvée.")
        return redirect('index')
    
    return render(request, 'restaurant/suivi_commande.html', {
        'commande': commande
    })


@login_required
def suivi_commandes(request):
    try:
        latest_commande = Commande.objects.filter(
            utilisateur=request.user
        ).latest('date')
        return render(request, 'restaurant/suivi_commandes.html', {
            'latest_commande': latest_commande
        })
    except Commande.DoesNotExist:
        return render(request, 'restaurant/suivi_commandes.html', {
            'latest_commande': None
        })
    
@login_required
def panier(request):
    panier = Panier.objects.filter(utilisateur=request.user, statut='actif').first()
    has_orders = Commande.objects.filter(utilisateur=request.user).exists()
    latest_commande = Commande.objects.filter(utilisateur=request.user).order_by('-date').first() if has_orders else None
    
    return render(request, 'restaurant/panier.html', {
        'panier': panier,
        'has_orders': has_orders,
        'latest_commande': latest_commande
    })

def index(request):
    return render(request, 'restaurant/index.html')

def detail_plat(request, plat_id):
    plat = get_object_or_404(Plat, id=plat_id)
    return render(request, 'restaurant/detail.html', {'plat': plat})

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    return Response({
        'articles': request.build_absolute_uri('articles/'),
        'plats': request.build_absolute_uri('plats/'),
        'panier': request.build_absolute_uri('panier/'),
        'commandes': request.build_absolute_uri('commandes/'),
    })

class PanierViewSet(viewsets.ModelViewSet):
    serializer_class = PanierSerializer
    permission_classes = [IsAuthenticated]
    queryset = Panier.objects.all()

    def get_queryset(self):
        # Ne renvoyer que les paniers de l'utilisateur connecté
        return Panier.objects.filter(utilisateur=self.request.user, statut='actif')

    def perform_create(self, serializer):
        # Associer le panier à l'utilisateur connecté lors de la création
        serializer.save(utilisateur=self.request.user)

    @action(detail=True, methods=['post'], url_path='add')
    def add_item(self, request, pk=None):
        """
        Ajouter un plat au panier
        Exemple: POST /api/panier/1/add/ {"plat_id": 1, "quantite": 2}
        """
        panier = self.get_object()
        plat_id = request.data.get('plat_id')
        quantite = request.data.get('quantite', 1)

        try:
            plat = Plat.objects.get(id=plat_id)
        except Plat.DoesNotExist:
            return Response({"detail": "Plat non trouvé."}, status=status.HTTP_404_NOT_FOUND)

        if not plat.disponibilite:
            return Response({"detail": "Plat non disponible."}, status=status.HTTP_400_BAD_REQUEST)

        # Vérifier si le plat est déjà dans le panier
        panier_item, created = PanierItem.objects.get_or_create(
            panier=panier,
            plat=plat,
            defaults={'quantite': quantite}
        )
        if not created:
            panier_item.quantite += int(quantite)
            panier_item.save()

        serializer = PanierItemSerializer(panier_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='clear')
    def clear(self, request, pk=None):
        """
        Vider le panier
        Exemple: POST /api/panier/1/clear/
        """
        panier = self.get_object()
        panier.items.all().delete()
        return Response({"detail": "Panier vidé avec succès."}, status=status.HTTP_204_NO_CONTENT)


class CommandeViewSet(viewsets.ModelViewSet):
    serializer_class = CommandeSerializer
    permission_classes = [IsAuthenticated]
    queryset = Commande.objects.all()
    

    def get_queryset(self):
        # Ne renvoyer que les commandes de l'utilisateur connecté
        return Commande.objects.filter(utilisateur=self.request.user)

    def perform_create(self, serializer):
        # Associer la commande à l'utilisateur connecté
        panier = Panier.objects.filter(utilisateur=self.request.user, statut='actif').first()
        if not panier or not panier.items.exists():
            raise serializers.ValidationError("Le panier est vide.")

        total = panier.calculer_total()
        serializer.save(
            utilisateur=self.request.user,
            total=total
        )

        # Marquer le panier comme terminé
        panier.statut = 'termine'
        panier.save()

    @action(detail=True, methods=['post'], url_path='confirmer')
    def confirmer(self, request, pk=None):
        """
        Confirmer une commande
        Exemple: POST /api/commandes/1/confirmer/
        """
        commande = self.get_object()
        if commande.statut != 'en_attente':
            return Response({"detail": "Commande déjà confirmée ou livrée."}, status=status.HTTP_400_BAD_REQUEST)
        
        commande.statut = 'confirmee'
        commande.save()
        return Response({"detail": "Commande confirmée avec succès."}, status=status.HTTP_200_OK)
    


class CategorieViewSet(viewsets.ModelViewSet):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

class PanierViewSet(viewsets.ModelViewSet):
    queryset = Panier.objects.all()
    serializer_class = PanierSerializer

class CommandeViewSet(viewsets.ModelViewSet):
    queryset = Commande.objects.all()
    serializer_class = CommandeSerializer

class PanierItemViewSet(viewsets.ModelViewSet):
    queryset = PanierItem.objects.all()
    serializer_class = PanierItemSerializer

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class CommentaireViewSet(viewsets.ModelViewSet):
    queryset = Commentaire.objects.all()
    serializer_class = CommentaireSerializer

class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer