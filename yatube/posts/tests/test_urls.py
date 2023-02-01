from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostUrlTest(TestCase):
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
            text='Тестовый пост!!!',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='NoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author = User.objects.get(username='auth')
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.author)
        self.main_page = '/'
        self.group_page = f'/group/{self.group.slug}/'
        self.profile_page = f'/profile/{self.user.username}/'
        self.post_veiw_page = f'/posts/{self.post.id}/'
        self.no_page = '/indexisting_page/'
        self.create_page = '/create/'
        self.post_edit_page = f'/posts/{self.post.id}/edit/'

    def test_pages_to_all_users(self):
        urls_name = {
            self.main_page: HTTPStatus.OK,
            self.group_page: HTTPStatus.OK,
            self.profile_page: HTTPStatus.OK,
            self.post_veiw_page: HTTPStatus.OK,
            self.no_page: HTTPStatus.NOT_FOUND,
            self.create_page: HTTPStatus.FOUND,
            self.post_edit_page: HTTPStatus.FOUND,
        }
        for address, code in urls_name.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, code)

    def test_pages_to_authorized_users(self):
        urls_name = {
            self.main_page: HTTPStatus.OK,
            self.group_page: HTTPStatus.OK,
            self.profile_page: HTTPStatus.OK,
            self.post_veiw_page: HTTPStatus.OK,
            self.no_page: HTTPStatus.NOT_FOUND,
            self.create_page: HTTPStatus.OK,
            self.post_edit_page: HTTPStatus.FOUND,
        }
        for address, code in urls_name.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, code)

    def test_pages_to_authorized_author_users(self):
        urls_name = {
            self.main_page: HTTPStatus.OK,
            self.group_page: HTTPStatus.OK,
            self.profile_page: HTTPStatus.OK,
            self.post_veiw_page: HTTPStatus.OK,
            self.no_page: HTTPStatus.NOT_FOUND,
            self.create_page: HTTPStatus.OK,
            self.post_edit_page: HTTPStatus.OK,
        }
        for address, code in urls_name.items():
            with self.subTest(address=address):
                response = self.authorized_client_author.get(address)
                self.assertEqual(response.status_code, code)

    def test_correct_template_to_all_users(self):
        templates_name = {
            self.main_page: 'posts/index.html',
            self.group_page: 'posts/group_list.html',
            self.profile_page: 'posts/profile.html',
            self.post_veiw_page: 'posts/post_detail.html',
            self.no_page: 'core/404.html',
        }
        for address, name in templates_name.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, name)

    def test_correct_template_to_authorized_users(self):
        templates_name = {
            self.main_page: 'posts/index.html',
            self.group_page: 'posts/group_list.html',
            self.profile_page: 'posts/profile.html',
            self.post_veiw_page: 'posts/post_detail.html',
            self.create_page: 'posts/create_post.html',
        }
        for address, name in templates_name.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, name)

    def test_correct_template_to_authorized_author_users(self):
        templates_name = {
            self.main_page: 'posts/index.html',
            self.group_page: 'posts/group_list.html',
            self.profile_page: 'posts/profile.html',
            self.post_veiw_page: 'posts/post_detail.html',
            self.create_page: 'posts/create_post.html',
            self.post_edit_page: 'posts/create_post.html',
        }
        for address, name in templates_name.items():
            with self.subTest(address=address):
                response = self.authorized_client_author.get(address)
                self.assertTemplateUsed(response, name)
