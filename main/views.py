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
    
    
    