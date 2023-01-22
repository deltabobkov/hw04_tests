from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField("page title", max_length=200)
    slug = models.SlugField("group id", unique=True)
    description = models.TextField("group description")

    class Meta:
        verbose_name = "group"
        verbose_name_plural = "groups"

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    STRING_LENGTH = 15
    text = models.TextField("Текс поста", help_text="Введите текст поста")
    pub_date = models.DateTimeField("date of publication", auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="post author",
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="posts",
        verbose_name="Группа",
        help_text="Связанная группа",
    )

    class Meta:
        verbose_name = "post"
        verbose_name_plural = "posts"
        ordering = ["-pub_date"]

    def __str__(self) -> str:
        return self.text[: Post.STRING_LENGTH]
