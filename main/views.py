from django.http import HttpResponseRedirect
from django.shortcuts import render
from beli_obat.views import validate_jwt_and_get_user

def home(request):
    token = request.COOKIES.get('jwt')

    if token is None:
        # return HttpResponseForbidden("Token tidak ditemukan. Silakan login.")
        is_authenticated = False
        context = {'is_authenticated': is_authenticated}
        return render(request, 'home.html', context)
    else:
        is_authenticated = True
        user, error = validate_jwt_and_get_user(token)

        if error:
            return error
    
        context = {'is_authenticated': is_authenticated, 'user': user}

        return render(request, 'home.html', context)
    


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

    
    
    