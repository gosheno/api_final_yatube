from rest_framework.response import Response
from rest_framework import viewsets, mixins, permissions, status
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.filters import SearchFilter
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.pagination import LimitOffsetPagination
import logging

from posts.models import Post, Group, Follow
from .serializers import (
    PostSerializer,
    CommentSerializer,
    GroupSerializer,
    FollowSerializer,
)
from .permissions import IsAuthorOrReadOnly

logger = logging.getLogger(__name__)
User = get_user_model()


class DynamicPagination(LimitOffsetPagination):
    def paginate_queryset(self, queryset, request, view=None):
        # Only paginate if 'limit' or 'offset' is present in query params
        if (
            "limit" not in request.query_params
            and "offset" not in request.query_params
        ):
            return None
        return super().paginate_queryset(queryset, request, view)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related("author", "group").all()
    serializer_class = PostSerializer
    pagination_class = DynamicPagination
    permission_classes = [permissions.AllowAny]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsAuthorOrReadOnly()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        queryset = super().get_queryset()
        group_id = self.request.query_params.get("group")
        author_id = self.request.query_params.get("author")

        if group_id is not None:
            queryset = queryset.filter(group=group_id)
        if author_id is not None:
            queryset = queryset.filter(author=author_id)
        return queryset

    def perform_create(self, serializer):
        try:
            serializer.save(author=self.request.user)
            logger.info(f"New post created by {self.request.user.username}")
        except Exception as e:
            logger.error(f"Error creating post: {str(e)}")
            raise

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly,
    ]
    pagination_class = None

    def get_queryset(self):
        post_id = self.kwargs.get("post_id")
        post = get_object_or_404(Post, id=post_id)
        return post.comments.select_related("author").all()

    def perform_create(self, serializer):
        post_id = self.kwargs.get("post_id")
        post = get_object_or_404(Post, id=post_id)
        serializer.save(author=self.request.user, post=post)

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return super().create(request, *args, **kwargs)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class FollowViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["following__username"]
    pagination_class = None

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user).select_related(
            "following")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
