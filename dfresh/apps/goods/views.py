from django.views.generic import View
from django.shortcuts import redirect, render, reverse


class GetAndSetIndexView(View):
    def get(self, request):
        return render(request, 'index.html')