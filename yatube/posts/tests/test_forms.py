from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username="user1",
        )
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            "text": self.post.text,
            "group": self.group.id,
        }
        response = self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response,
            reverse("posts:profile", args=(self.user.username,)),
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text="Тестовый пост", group=self.group.id
            ).exists()
        )

    def test_edit_post(self):
        """Редактирование поста с указанным post_id"""
        posts_count = Post.objects.count()
        form_data = {
            "text": "Отредактированный текст",
            "author": self.user,
            "group": self.group.id,
        }
        response = self.authorized_client.post(
            reverse("posts:post_edit", args=(self.post.id,)),
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response, reverse("posts:post_detail", args=(self.post.id,))
        )
        edit_post = Post.objects.last()
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(edit_post.text, "Отредактированный текст")
        self.assertEqual(edit_post.author, self.user)
