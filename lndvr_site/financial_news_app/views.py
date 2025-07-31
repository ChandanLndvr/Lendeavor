from django.shortcuts import render, redirect
from financial_news_app.models import Financial_news
from financial_news_app.serializers import Financial_news_serializers
from django.urls import reverse
from myapp.models import SignUp
from django.shortcuts import get_object_or_404
# Create your views here.


#------------------------- Financial News --------------------------

def financial_news(request):
    financial_data = Financial_news.objects.all()
    message = request.GET.get('message')
    error = request.GET.get('error')
    print(financial_data)
    context = {
        'financial_data': financial_data, 
        'current_page':'financial_news',
        'message': message,
        'error': error
    }
    return render(request, 'financial_news.html', context)
        


def add_news(request):
    if request.method == "POST":
        try:
            added_by_email = request.POST.get('added_by')
            added_by_user = None
            if added_by_email:
                added_by_user = get_object_or_404(SignUp, Email=added_by_email)

            cleaned_data = {
                'Title': request.POST.get('title'),
                'Date_publish': request.POST.get('date_publish'),
                'Content': request.POST.get('content'),
                'Summary': request.POST.get('summary'),
                'Added_by': added_by_user.pk if added_by_user else None,
                'Active': request.POST.get('active') == 'on',
            }
            print("cleaned data", cleaned_data)

            if 'thumbnail' in request.FILES:
                cleaned_data['Thumbnail'] = request.FILES['thumbnail']

            serializer = Financial_news_serializers(data=cleaned_data)
            print(serializer)

            if serializer.is_valid():
                serializer.save()
                return redirect(f"{reverse('financial_news')}?message=News added successfully!")

            else:
                print(serializer.errors)  
                return redirect(f"{reverse('addNews')}?error=Something went wrong!")

        except Exception as e:
            return render(request, 'add_news.html', {
                'error': str(e),
                'current_page': 'financial_news'
            })

    return render(request, 'add_news.html', {
        'current_page': 'financial_news'
    })
