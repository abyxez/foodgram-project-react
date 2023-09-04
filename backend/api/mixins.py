from django.db.models import Model, Q
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST)


class CreateDeleteViewMixin():
    add_serializer: ModelSerializer
    link_model: Model

    def create_relation_recipe(self, obj_id) -> Response:
        obj = get_object_or_404(self.queryset, pk=obj_id)
        try:
            self.link_model(None, recipe=obj, user=self.request.user).save()
        except IntegrityError:
            return Response(
                {'error': 'Действие невозможно выполнить.'},
                status=HTTP_400_BAD_REQUEST,
            )

        serializer = self.add_serializer(obj)
        return Response(serializer.data, status=HTTP_201_CREATED)

    def create_relation_user(self, obj_id) -> Response:
        obj = get_object_or_404(self.queryset, pk=obj_id)
        try:
            self.link_model(None, author=obj, user=self.request.user).save()
        except IntegrityError:
            return Response(
                {'error': 'Действие невозможно выполнить.'},
                status=HTTP_400_BAD_REQUEST,
            )

        serializer = self.add_serializer(obj)
        return Response(serializer.data, status=HTTP_201_CREATED)

    def delete_relation(self, q: Q) -> Response:
        to_delete = (
            self.link_model.objects.filter(q & Q(user=self.request.user))
            .first()
            .delete()
        )
        if not to_delete:
            return Response(
                {'error': 'Действие невозможно выполнить.'},
                status=HTTP_400_BAD_REQUEST
            )

        return Response(status=HTTP_204_NO_CONTENT)
