"""Test mixins"""

from django.core.urlresolvers import reverse
from rest_framework_json_api import mixins
from tests import models
from tests.utils import dump_json
from tests.views import PostViewSet
import pytest

pytestmark = pytest.mark.django_db


def test_drf_put_partial_fails(rf):
    author = models.Person.objects.create(name="Author")
    post = models.Post.objects.create(author=author, title="old_title")
    data = dump_json({
        "posts": {
            "title": "new_title"
        }
    })
    result_data = {
        "author": ["This field is required."]
    }

    request = rf.put(
        reverse("post-detail", kwargs={'pk': post.pk}), data=data,
        content_type="application/vnd.api+json")
    view = PostViewSet.as_view({'put': 'update'})
    response = view(request, pk=post.pk)
    response.render()

    assert response.status_code == 400
    assert response.data == result_data


def test_json_api_put_partial_success(rf):

    class PartialPutPostViewSet(mixins.PartialPutMixin, PostViewSet):
        pass

    author = models.Person.objects.create(name="Author")
    post = models.Post.objects.create(author=author, title="old_title")
    data = dump_json({
        "posts": {
            "title": "new_title"
        }
    })
    result_data = {
        "id": post.pk,
        "url": "http://testserver/posts/%d/" % post.pk,
        "title": "new_title",
        "author": "http://testserver/people/%d/" % author.pk,
        "comments": [],
    }

    request = rf.put(
        reverse("post-detail", kwargs={'pk': post.pk}), data=data,
        content_type="application/vnd.api+json")
    view = PartialPutPostViewSet.as_view({'put': 'update'})
    response = view(request, pk=post.pk)
    response.render()

    assert response.status_code == 200
    assert response.data == result_data
