from django.shortcuts import render
from django.views.decorators.http import require_GET

@require_GET
def index(request, lang='ru'):
    return render(request, 'index.html', context={'lang': lang})