from django.shortcuts import render, get_object_or_404
from .models import Article

def home(request):
    articles = Article.objects.all().order_by('-publish_date')[:5]
    return render(request, 'home.html', {'articles': articles})

def article_detail(request, id):
    article = get_object_or_404(Article, id=id)
    return render(request, 'main/article_detail.html', {
        'article': article,
        'sections': article.sections.all().order_by('order')
    })

def article1(request):
    return render(request, 'article1.html')
def article2(request):
    return render(request, 'article2.html')
def article3(request):
    return render(request, 'article3.html')
def article4(request):
    return render(request, 'article4.html')
def article5(request):
    return render(request, 'article5.html')