from django.shortcuts import render


# Create your views here.

from .forms import BranchForm
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response


@api_view(['POST'])
def create_branch(request):
    form = BranchForm()

    if request.method == 'POST':
        form = BranchForm(request.POST, request.FILES)
        if form.is_valid():
            branch = form.save(commit=False)
            branch.save()
            return Response(True)

    context = {'form': form}
    return Response(context)
