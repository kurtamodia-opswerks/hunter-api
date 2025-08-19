import time
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework import viewsets, permissions, filters
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from api.models import Dungeon
from api.serializers import (
    DungeonSerializer,
    DungeonCreateSerializer
)
from api.filters import ActiveDungeonFilterBackend



class DungeonViewSet(viewsets.ModelViewSet):
    queryset = Dungeon.objects.prefetch_related(
        'raids', 'raids__participations', 'raids__participations__hunter'
    ).all()
    serializer_class = DungeonSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    filter_backends = [ActiveDungeonFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'location']
    ordering_fields = ['name', 'rank']

    @method_decorator(cache_page(60 * 15, key_prefix='dungeon_list'))
    @method_decorator(vary_on_headers('Authorization'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def get_queryset(self):
        time.sleep(2)
        qs = super().get_queryset()
        return qs

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PUT'):
            return DungeonCreateSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        dungeon = serializer.save()