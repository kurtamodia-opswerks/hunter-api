import time
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework import viewsets, permissions, filters
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from api.models import Hunter
from api.serializers import (
    HunterSerializer,
    HunterCreateSerializer,
)
from api.filters import HunterFilter
from api.tasks import (
    send_hunter_welcome_email
)



class HunterViewSet(viewsets.ModelViewSet):
    queryset = Hunter.objects.select_related('guild') \
        .prefetch_related('skills', 'completed_raids', 'participations', 'participations__raid') \
        .all()
    serializer_class = HunterSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = HunterFilter
    search_fields = ['username', 'first_name', 'last_name']
    ordering_fields = ['date_joined', 'rank']

    @method_decorator(cache_page(60 * 15, key_prefix='hunter_list'))
    @method_decorator(vary_on_headers('Authorization'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        hunter = serializer.save()
        send_hunter_welcome_email.delay(hunter.id)
    
    def get_queryset(self):
        time.sleep(2)
        qs = super().get_queryset()
        return qs

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PUT'):
            return HunterCreateSerializer
        return super().get_serializer_class()
    
    def get_permissions(self):  
        self.permission_classes = [permissions.AllowAny]
        if self.request.method in ('POST', 'PUT', 'DELETE'):
            self.permission_classes = [permissions.IsAdminUser]
        return super().get_permissions()