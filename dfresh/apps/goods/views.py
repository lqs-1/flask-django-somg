from django.shortcuts import render
from django.views.generic import View
# Create your views here.


class GetIndexView(View):
    def get(self, request):
        return render(request=request, template_name='index.html')