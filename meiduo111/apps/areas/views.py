from django.shortcuts import render

from rest_framework import generics
from .models import Area
from .serializers import AreaSerializer,AreaSubSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet


class AreaViewSet(ReadOnlyModelViewSet):
    def get_queryset(self):
        if self.action == 'list':
            return Area.objects.filter(parent__isnull=True)
        else:
            return Area.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return AreaSerializer
        else:
            return AreaSubSerializer
