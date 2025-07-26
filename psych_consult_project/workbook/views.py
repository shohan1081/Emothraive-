from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from .models import Workbook, FavoriteWorkbook
from .serializers import WorkbookSerializer, WorkbookBannerSerializer, FavoriteWorkbookSerializer
from subscriptions.models import UserSubscription
from music.permissions import IsOwnerOrReadOnly # Assuming this permission exists or needs to be created

class WorkbookListView(generics.ListAPIView):
    queryset = Workbook.objects.all().order_by('-created_at')

    def get_serializer_class(self):
        user = self.request.user
        if user.is_authenticated:
            try:
                # Check for the latest active subscription
                subscription = user.subscriptions.latest('end_date')
                if subscription.is_active():
                    return WorkbookSerializer
            except UserSubscription.DoesNotExist:
                pass  # User is authenticated but has no subscription
        return WorkbookBannerSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        category_name = self.request.query_params.get('category')
        if category_name:
            queryset = queryset.filter(category__name__iexact=category_name)
        return queryset

class FavoriteWorkbookViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteWorkbookSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly] # Assuming IsOwnerOrReadOnly is available

    def get_queryset(self):
        return FavoriteWorkbook.objects.filter(user=self.request.user).prefetch_related('workbooks')

    def get_object(self):
        # Get or create the user's single favorite workbook list
        favorite_workbook, created = FavoriteWorkbook.objects.get_or_create(user=self.request.user)
        return favorite_workbook

    def list(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_workbook(self, request):
        favorite_workbook = self.get_object()
        workbook = Workbook.objects.get(pk=request.data.get('workbook_id'))
        favorite_workbook.workbooks.add(workbook)
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def remove_workbook(self, request):
        favorite_workbook = self.get_object()
        workbook = Workbook.objects.get(pk=request.data.get('workbook_id'))
        favorite_workbook.workbooks.remove(workbook)
        return Response(status=status.HTTP_200_OK)