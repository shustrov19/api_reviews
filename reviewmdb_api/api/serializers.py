from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.relations import SlugRelatedField
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User
from users.utils import send_confirmation_code

from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django.shortcuts import get_object_or_404


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )


class UserCreateSerializer(serializers.Serializer):
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+$',
        max_length=150,
    )
    email = serializers.EmailField(
        max_length=254,
    )

    def create(self, validated_data):
        user, _ = User.objects.get_or_create(**validated_data)
        send_confirmation_code(
            email=user.email,
            confirmation_code=default_token_generator.make_token(user)
        )
        return user

    # добавили метод exists(), но конструкцию не меняли,
    # т.к по-другому проверка pytest выдает ошибки
    def validate(self, data):
        is_username = User.objects.filter(username=data['username']).exists()
        is_email = User.objects.filter(email=data['email']).exists()
        if data.get('username') == 'me':
            raise serializers.ValidationError(
                'Использовать имя me запрещено'
            )
        if is_username and not is_email:
            raise serializers.ValidationError(
                'Пользователь с таким username уже существует'
            )
        if is_email and not is_username:
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует'
            )
        return data


class UserTokenSerializer(serializers.Serializer):
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+$',
        max_length=150,
        required=True
    )
    confirmation_code = serializers.CharField(
        max_length=150,
        required=True
    )

    def validate(self, data):
        username = data['username']
        confirmation_code = data['confirmation_code']
        user = get_object_or_404(User, username=username)
        if not default_token_generator.check_token(user, confirmation_code):
            raise serializers.ValidationError(
                '{confirmation_code}: Код подтверждения не верный.'
            )

    def create(self, validated_data):
        username = validated_data['username']
        user = get_object_or_404(User, username=username)
        return {'token': str(AccessToken.for_user(user))}


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('slug', 'name')
        model = Category


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('slug', 'name')
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True, queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category'
        )


class ReadOnlyTitleSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField(read_only=True)
    genre = GenreSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )

    def get_rating(self, obj):
        return obj.reviews.all().aggregate(Avg('score'))['score__avg']


class CommentSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if request.method == 'POST':
            if Review.objects.filter(title=title, author=author).exists():
                raise ValidationError('Нельзя одному автору оставлять больше '
                                      'одного отзыва на одно произведение')
        return data
