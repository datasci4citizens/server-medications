from django.shortcuts import render
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view
from rest_framework.response import Response

# add user, remove user, edit user, get user

@api_view(['GET'])
def index(request):
    return Response("OK")

# add drug, remove drug, edit drug, get drug