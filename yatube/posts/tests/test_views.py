import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
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

        cls.group_1 = Group.objects.create(
            title='Тестовая 1',
            slug='test-slug_1',
            description='Тестовое 1',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост!!!',
            group=cls.group,
        )
        objs_group = [Post(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост ' + str(i)) for i in range(14)
        ]
        Post.objects.bulk_create(objs_group)
        objs_group_1 = [Post(
            author=cls.user,
            group=cls.group_1,
            text='Тестовый пост 111_' + str(i)) for i in range(3)
        ]
        Post.objects.bulk_create(objs_group_1)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.not_follower = User.objects.create_user(username='AnyName')
        self.authorized_not_follower_client = Client()
        self.authorized_not_follower_client.force_login(self.not_follower)
        self.new_user = User.objects.create_user(username='NoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.new_user)
        self.author = User.objects.get(username='auth')
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.author)
        self.main_page = 'posts:index'
        self.group_page = 'posts:group_list'
        self.profile_page = 'posts:profile'
        self.post_veiw_page = 'posts:post_detail'
        self.create_page = 'posts:post_create'
        self.post_edit_page = 'posts:post_edit'
        self.post_comment = 'posts:add_comment'
        self.post_follow_index = 'posts:follow_index'
        self.post_follow = 'posts:profile_follow'
        self.post_unfollow = 'posts:profile_unfollow'
        self.posts_on_finsl_main_page = (
            len(Post.objects.all()) % settings.POSTS_ON_PAGE)
        self.posts_on_finsl_author_page = (
            len(self.author.posts.all()) % settings.POSTS_ON_PAGE)
        self.posts_on_finsl_group_page = (
            len(self.group.posts.all()) % settings.POSTS_ON_PAGE)

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            reverse(self.main_page): 'posts/index.html',
            (reverse(self.group_page,
                     kwargs={'slug': self.group.slug})):
            'posts/group_list.html',
            (reverse(self.profile_page,
                     kwargs={'username': self.author.username})):
            'posts/profile.html',
            (reverse(self.post_veiw_page,
                     kwargs={'post_id': self.post.id})):
            'posts/post_detail.html',
            reverse(self.create_page): 'posts/create_post.html',
            (reverse(self.post_edit_page,
                     kwargs={'post_id': self.post.id})):
            'posts/create_post.html',
        }
        for address, name in templates_pages_names.items():
            with self.subTest(address=address):
                response = self.authorized_client_author.get(address)
                self.assertTemplateUsed(response, name)

    def test_first_page_contains_ten_records(self):
        quantity_on_pages = {
            reverse(self.main_page): settings.POSTS_ON_PAGE,
            (reverse(self.group_page,
                     kwargs={'slug': self.group.slug})):
            settings.POSTS_ON_PAGE,
            (reverse(self.profile_page,
                     kwargs={'username': self.author.username})):
            settings.POSTS_ON_PAGE,
        }
        for address, number in quantity_on_pages.items():
            with self.subTest(address=address):
                response = self.authorized_client_author.get(address)
                self.assertEqual(len(response.context['page_obj']), number)

    def test_second_page_contains_records(self):
        quantity_on_pages = {
            reverse(self.main_page): self.posts_on_finsl_main_page,
            (reverse(self.group_page,
                     kwargs={'slug': self.group.slug})):
            self.posts_on_finsl_group_page,
            (reverse(self.profile_page,
                     kwargs={'username': self.author.username})):
            self.posts_on_finsl_author_page,
        }
        for address, number in quantity_on_pages.items():
            with self.subTest(address=address):
                response = self.authorized_client_author.get(
                    address + '?page=2')
                self.assertEqual(len(response.context['page_obj']), number)

    def test_pages_for_correct_info(self):
        info_on_pages = {
            reverse(self.main_page):
            list(Post.objects.all()[:settings.POSTS_ON_PAGE]),
            reverse(self.group_page, kwargs={'slug': self.group.slug}):
            list(Post.objects.filter(
                group_id=self.group.id)[:settings.POSTS_ON_PAGE]),
            reverse(self.profile_page, kwargs={'username':
                                               self.author.username}):
            list(Post.objects.filter(
                author_id=self.user.id)[:settings.POSTS_ON_PAGE]),
        }
        for address, info in info_on_pages.items():
            with self.subTest(address=address):
                response = self.authorized_client_author.get(address)
                self.assertEqual(list(response.context['page_obj']), info)

    def test_page_post_detail_for_correct_info(self):
        response = self.authorized_client_author.get(
            reverse(self.post_veiw_page, kwargs={'post_id': self.post.id}))
        self.assertEqual((response.context['post']),
                         Post.objects.get(id=self.post.id))

    def test_page_post_create_for_correct_info(self):
        response = self.authorized_client_author.get(
            reverse(self.create_page))
        resp_context = response.context['form']
        self.assertEqual(list(resp_context.fields), [
                         'text', 'group'])
        self.assertNone(resp_context['text'].value())
        self.assertNone(resp_context['group'].value())

    def test_page_post_create_for_correct_info(self):
        response = self.authorized_client_author.get(
            reverse(self.post_edit_page, kwargs={'post_id': self.post.id}))
        resp_context = response.context['form']
        self.assertEqual(list(resp_context.fields), [
                         'text', 'group', 'image'])
        self.assertEqual(resp_context['text'].value(),
                         Post.objects.get(id=self.post.id).text)
        self.assertEqual(resp_context['group'].value(),
                         Post.objects.get(id=self.post.id).group_id)

    def test_pages_for_correct_info_another_group(self):
        info_on_pages = {
            reverse(self.main_page): list(self.group_1.posts.all()),
            reverse(self.group_page, kwargs={'slug': self.group_1.slug}):
            list(self.group_1.posts.all()),
            reverse(self.profile_page, kwargs={'username':
                                               self.author.username}):
            list(self.group_1.posts.all()),
        }
        for address, info in info_on_pages.items():
            with self.subTest(address=address):
                response = self.authorized_client_author.get(address)
                for i in range(len(info)):
                    self.assertIn(info[i], list(response.context['page_obj']))

    def test_image_in_context(self):
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='posts/small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Текст из формы525',
            'group': self.group.id,
            'image': uploaded,
        }
        self.authorized_client_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        first_post = Post.objects.first()
        first_post_index = 0
        response = self.authorized_client_author.get(
            reverse(self.post_veiw_page, kwargs={'post_id': first_post.id}))
        self.assertEqual((response.context.get('post').image),
                         first_post.image)
        image_on_pages = {
            reverse(self.main_page): first_post.image,
            (reverse(self.group_page,
                     kwargs={'slug': self.group.slug})):
            first_post.image,
            (reverse(self.profile_page,
                     kwargs={'username': self.author.username})):
            first_post.image,
        }
        for address, image in image_on_pages.items():
            with self.subTest(address=address):
                response = self.authorized_client_author.get(address)
                self.assertEqual(list(response.context['page_obj'])[
                                 first_post_index].image, image)

    def test_can_comment_post(self):
        first_post = Post.objects.first()
        first_comment_index = 0
        form_data = {
            'text': 'Новый комментарий от авторизованного пользователя.',
        }
        self.authorized_client.post(
            reverse(self.post_comment, kwargs={'post_id': first_post.id}),
            data=form_data,
            follow=True
        )
        response = self.authorized_client.get(
            reverse(self.post_veiw_page, kwargs={'post_id': first_post.id})
        )
        self.assertEqual(list(response.context.get('comments'))[
                         first_comment_index].text, form_data['text'])

    def test_main_page_cache(self):
        response_first = self.authorized_client.get(reverse(self.main_page))
        Post.objects.first().delete()
        response_second = self.authorized_client.get(reverse(self.main_page))
        self.assertEqual(response_first.content, response_second.content)
        cache.clear()
        response_third = self.authorized_client.get(reverse(self.main_page))
        self.assertNotEqual(response_first.content, response_third.content)

    def test_can_follow_and_unfollow(self):
        count_follow = Follow.objects.all().count()
        self.authorized_client.get(reverse(self.post_follow, kwargs={
                                   'username': self.author.username}))
        self.assertEqual(Follow.objects.all().count(), count_follow + 1)
        self.authorized_client.get(reverse(self.post_unfollow, kwargs={
                                   'username': self.author.username}))
        self.assertEqual(Follow.objects.all().count(), count_follow)

    def test_new_post_in_feed_followers(self):
        self.authorized_client.get(reverse(self.post_follow, kwargs={
                                   'username': self.author.username}))
        post_for_folower = Post.objects.create(
            author=self.author,
            text='Новый пост для подписчиков!!!',
            group=self.group_1,
        )
        first_post_index = 0
        response_follower = self.authorized_client.get(
            reverse(self.post_follow_index))
        self.assertEqual(list(response_follower.context['page_obj'])[
            first_post_index], post_for_folower)
        response_not_follower = self.authorized_not_follower_client.get(
            reverse(self.post_follow_index))
        self.assertNotContains(response_not_follower, post_for_folower)
