from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
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
        self.authorized_client.force_login(PostPagesTests.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            "posts/index.html": reverse("posts:index"),
            "posts/group_list.html": reverse(
                "posts:group_list", kwargs={"slug": f"{self.group.slug}"}
            ),
            "posts/profile.html": reverse(
                "posts:profile", kwargs={"username": f"{self.user.username}"}
            ),
            "posts/post_detail.html": reverse(
                "posts:post_detail", kwargs={"post_id": f"{self.post.id}"}
            ),
            "posts/create_post.html": reverse("posts:post_create"),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_uses_correct_template(self):
        """URL-адрес редактирования поста использует соответствующий шаблон."""
        response = self.authorized_client.get(
            reverse("posts:post_edit", kwargs={"post_id": f"{self.post.id}"})
        )
        self.assertTemplateUsed(response, "posts/create_post.html")

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:index"))
        first_object = response.context["page_obj"][0]
        post_author = first_object.author
        post_text = first_object.text
        post_group = first_object.group
        self.assertEqual(post_author, self.user)
        self.assertEqual(post_text, "Тестовый пост")
        self.assertEqual(post_group, self.group)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:group_list", kwargs={"slug": f"{self.group.slug}"})
        )
        first_object = response.context["page_obj"][0]
        second_object = response.context["group"]
        post_author = first_object.author
        post_text = first_object.text
        post_group = first_object.group
        group_title = second_object.title
        group_description = second_object.description
        self.assertEqual(post_author, self.user)
        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post_group, self.group)
        self.assertEqual(group_title, self.group.title)
        self.assertEqual(group_description, self.group.description)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                "posts:profile", kwargs={"username": f"{self.user.username}"}
            )
        )
        first_object = response.context["page_obj"][0]
        post_author = first_object.author
        post_text = first_object.text
        post_group = first_object.group
        self.assertEqual(post_author, self.user)
        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post_group, self.group)
        self.assertEqual(response.context.get("posts_num"), 1)
        self.assertEqual(response.context.get("author"), self.user)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:post_detail", kwargs={"post_id": f"{self.post.id}"})
        )
        self.assertEqual(response.context.get("post").author, self.user)
        self.assertEqual(response.context.get("post").text, self.post.text)
        self.assertEqual(response.context.get("post").group, self.group)
        self.assertEqual(response.context.get("posts_count"), 1)

    def test_create_page_show_correct_context(self):
        """Шаблон create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:post_create"))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_page_show_correct_context(self):
        """Шаблон create для редактирования поста сформирован
        с правильным контекстом.
        """
        response = self.authorized_client.get(
            reverse("posts:post_edit", kwargs={"post_id": f"{self.post.id}"})
        )
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_created_post_with_group(self):
        """При создании поста с указанной группой,
        пост появляется на нужных страницах
        """
        pages = {
            "posts:index": {},
            "posts:group_list": {"slug": self.group.slug},
            "posts:profile": {"username": self.user.username},
        }
        for page, args in pages.items():
            with self.subTest(page=page):
                response = self.authorized_client.get(
                    reverse(page, kwargs=args)
                )
                first_object = response.context["page_obj"][0]
                post_text = first_object.text
                post_group = first_object.group
                self.assertEqual(post_text, self.post.text)
                self.assertEqual(post_group, self.group)
                self.assertNotEqual(post_group, "Другая группа")


class PaginatorViewsTest(TestCase):
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
        cls.post: list = []
        for i in range(13):
            cls.post.append(
                Post(
                    author=cls.user,
                    text=f"Тестовый пост {i}",
                    group=cls.group,
                )
            )
        Post.objects.bulk_create(cls.post)

        cls.pages = {
            "posts:index": {},
            "posts:group_list": {"slug": cls.group.slug},
            "posts:profile": {"username": cls.user.username},
        }

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(PaginatorViewsTest.user)

    def test_index_first_page_contains_ten_records(self):
        for page, args in self.pages.items():
            with self.subTest(page=page):
                response = self.author_client.get(reverse(page, kwargs=args))
                self.assertEqual(len(response.context["page_obj"]), 10)

    def test_index_second_page_contains_three_records(self):
        for page, args in self.pages.items():
            with self.subTest(page=page):
                response = self.author_client.get(
                    reverse(page, kwargs=args) + "?page=2"
                )
                self.assertEqual(len(response.context["page_obj"]), 3)
