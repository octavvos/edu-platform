from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from apps.catalog import services
from apps.catalog.models import Category, Review
from apps.catalog.serializers import CategorySerializer, ReviewSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["course"]

    def get_queryset(self):
        qs = Review.objects.select_related("user", "course")
        if self.request.method in permissions.SAFE_METHODS:
            return qs.filter(is_published=True)
        return qs.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            review = services.create_review(
                user=request.user,
                course=serializer.validated_data["course"],
                rating=serializer.validated_data["rating"],
                comment=serializer.validated_data.get("comment", ""),
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        return Response(self.get_serializer(review).data, status=status.HTTP_201_CREATED)
