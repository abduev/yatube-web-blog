from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views.generic import CreateView

from .forms import CreationForm


class SignUp(CreateView):
    """Класс регистрации пользователя"""
    form_class = CreationForm
    success_url = reverse_lazy("login")
    template_name = "signup.html"

    def form_valid(self, form):
        """Функция автоматической аутентификации пользователя
        после регистрации"""
        form.save()
        user = authenticate(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password1'],
        )
        login(self.request, user)
        return HttpResponseRedirect(reverse('index'))
