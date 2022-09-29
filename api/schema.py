import graphene
from graphene_django import DjangoObjectType
from django.core.exceptions import ObjectDoesNotExist
from .models import Director, Movie
import graphql_jwt
from graphql_jwt.decorators import login_required

class MovieType(DjangoObjectType):
    class Meta:
        model = Movie

    movie_age = graphene.String()
    def resolve_movie_age(self,info,  **kwargs):
        return "Old movie" if self.year < 2000 else  "New Movie"


class DirectorType(DjangoObjectType):
    class Meta:
        model = Director

class Query(graphene.ObjectType):
    all_movies = graphene.List(MovieType)
    all_directors = graphene.List(DirectorType)
    movie = graphene.Field(MovieType, id=graphene.Int(), title = graphene.String())
    
    @login_required
    def resolve_all_movies(self, info, **kwargs):
        return Movie.objects.all()
    
    def resolve_all_directors(self, info, **kwargs):
        return Director.objects.all()

    def resolve_movie(self, info, **kwargs):
        id = kwargs.get('id')
        title = kwargs.get('title')

        if id is not None:
            return Movie.objects.get(pk=id)

        if title is not None:
            return Movie.objects.get(title=title)

        return None

class MovieCreateMutation(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        year = graphene.Int(required=True)
    
    movie = graphene.Field(MovieType)

    def mutate(self, info, title, year):
        movie = Movie.objects.create(title=title, year=year)

        return MovieCreateMutation(movie=movie)

class UpdateMovieMutation(graphene.Mutation):
    class Arguments:
        title = graphene.String()
        year = graphene.Int()
        movie_id = graphene.ID(required=True) 

    movie = graphene.Field(MovieType)

    def mutate(self, info, title, year, movie_id):
        try:
            movie = Movie.objects.get(pk=movie_id)
            if title:
                movie.title = title
            if year:
                movie.year = year
            movie.save()
        except ObjectDoesNotExist:
            return None
        
        return MovieCreateMutation(movie=movie)

class DeleteMovieMutation(graphene.Mutation):
    class Arguments:
        movie_id = graphene.ID(required=True) 

    movie = graphene.Field(MovieType)

    def mutate(self, info, movie_id):
        movie = Movie.objects.get(pk=movie_id)
        movie.delete()
    
        return MovieCreateMutation(movie=None)

class Mutation:
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    create_movie = MovieCreateMutation.Field()
    update_movie = UpdateMovieMutation.Field()
    delete_movie = DeleteMovieMutation.Field()
