from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy

class LogoutGetAllowedView(LogoutView):
    # on redirige vers la page d’accueil après logout
    next_page = reverse_lazy('home')

    # accepter aussi le GET en appelant post()
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
