from django.shortcuts import render
from financial_news_app.models import Financial_news

# Create your views here.


#------------------------- Financial News --------------------------

def financial_news(request):
    if request.method == "POST":
        try:
            financial_data = Financial_news.objects.all()
            return render('financial_news.html',{'financial_data': financial_data, 'success':'Data added successfully!'})
            
        except Exception as e:
            return render('financial_news.html',{'error': str(e)})
        
    return render(request, 'financial_news.html', {'current_page':'financial_news'})


def add_news(request):
    return render(request, 'add_news.html')