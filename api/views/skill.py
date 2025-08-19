import time
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework import viewsets, permissions, filters
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from api.models import Skill
from api.serializers import (
    SkillSerializer
)
from api.filters import SkillFilter




class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = SkillFilter
    search_fields = ['name']
    ordering_fields = ['name', 'power']

    @method_decorator(cache_page(60 * 15, key_prefix='skill_list'))
    @method_decorator(vary_on_headers('Authorization'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def get_queryset(self):
        time.sleep(2)
        qs = super().get_queryset()
        return qs
    
    def get_permissions(self):  
        self.permission_classes = [permissions.AllowAny]
        if self.request.method in ('POST', 'PUT', 'DELETE'):
            self.permission_classes = [permissions.IsAdminUser]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        skill = serializer.save()