from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        labels = {'text': 'Текст поста', 'group': 'Группа'}
        help_texts = {'text': 'Текст нового поста',
                      'group': 'Группа, к которой будет относиться пост'}
        fields = ['text', 'group', 'image']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        labels = {'text': 'Текст комментария'}
        help_texts = {'text': 'Текст нового комментария'}
        fields = ['text']
