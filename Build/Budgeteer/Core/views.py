from django.shortcuts import render
from .models import user_data, get_receipt_data

def frontpage(request):
    return render(request, 'Core/frontpage.html')

def dashboard(request):
    obj = get_receipt_data.objects.all()
    context = {
        "object": obj
    }
    return render(request, 'Core/dashboard.html', context)

def contact(request):
    return render(request, 'Core/contact.html')
