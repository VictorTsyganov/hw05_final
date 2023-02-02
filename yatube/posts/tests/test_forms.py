import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост ',
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='NoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(PostFormTest.user)
        self.comment_redirect = ('/auth/login/?next=/posts/'
                                 f'{PostFormTest.post.id}/comment/')

    def test_can_create_new_post_with_image(self):
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='posts/small_1.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Текст из формы',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        first_post = Post.objects.first()
        self.assertRedirects(
            response, (reverse('posts:profile', kwargs={
                       'username': self.user.username}))
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(first_post.text, form_data['text'])
        self.assertEqual(first_post.group.id, form_data['group'])
        self.assertEqual(first_post.author, self.user)
        self.assertIn(uploaded.name, first_post.image.name.split('/'))

    def test_can_change_post(self):
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='posts/small_2.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовая группа + Текст из формы',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client_author.post(
            (reverse('posts:post_edit',
                     kwargs={'post_id': self.post.id})),
            data=form_data,
            follow=True
        )
        changed_post = Post.objects.get(id=self.post.id)
        self.assertRedirects(response, (reverse('posts:post_detail',
                                        kwargs={'post_id': self.post.id})))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(changed_post.text, form_data['text'])
        self.assertEqual(changed_post.group.id, form_data['group'])
        self.assertEqual(changed_post.author, PostFormTest.user)
        self.assertIn(uploaded.name, changed_post.image.name.split('/'))

    def test_can_not_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Новый пост от не авторизованного пользователя.',
            'group': self.group.id,
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, (reverse('users:login')
                       + '?next=' + reverse('posts:post_create'))
        )
        self.assertEqual(Post.objects.count(), posts_count)

    def test_can_comment_post(self):
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Новый комментарий от авторизованного пользователя.',
        }
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={
                    'post_id': PostFormTest.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)

    def test_can_not_comment_post(self):
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Новый комментарий от не авторизованного пользователя.',
        }
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={
                    'post_id': PostFormTest.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.comment_redirect)
        self.assertEqual(Comment.objects.count(), comments_count)
