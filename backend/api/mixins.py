from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from recipes.models import Recipe
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.viewsets import GenericViewSet

User = get_user_model()


class CreateDestroyViewSet(CreateModelMixin, DestroyModelMixin,
                           GenericViewSet):

    def perform_create(self, serializer):
        user = self.request.user
        if self.kwargs.get('author_id'):
            author = get_object_or_404(User, pk=self.kwargs.get('author_id'))
            serializer.save(user=user, author=author)
        else:
            recipe = get_object_or_404(Recipe, pk=self.kwargs.get('recipe_id'))
            serializer.save(user=user, recipe=recipe)

    @action(methods=['delete'], detail=True)
    def delete(self, request, recipe_id=None, author_id=None):
        if author_id:
            get_object_or_404(
                self.serializer_class.Meta.model,
                author=author_id,
                user=request.user,
            ).delete()
            return Response(status=HTTP_204_NO_CONTENT)
        get_object_or_404(
            self.serializer_class.Meta.model,
            recipe=recipe_id,
            user=request.user,
        ).delete()
        return Response(status=HTTP_204_NO_CONTENT)
