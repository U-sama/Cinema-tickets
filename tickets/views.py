from django.shortcuts import render
from django.http.response import JsonResponse
from .models import Guest, Movie, Reservation, Post
from rest_framework.decorators import api_view
from .serializers import GuestSerializer, MovieSerializer, ResevationSerializer, PostSerializer
from rest_framework import status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import Http404
from rest_framework import generics, mixins, viewsets

from rest_framework.authentication import BasicAuthentication ,TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .permissions import IsauthorOrReadOnly


# Create your views here.

#1 with no rest and no model query (FVB)
def no_rest_no_model(request):
    guests = [
        {
            "id":1,
            "name": "Osama",
            "mobile":7847785

        },
        {
            "id":2,
            "name": "Mohamed",
            "mobile":9548798
        }
    ]
    return JsonResponse(guests, safe=False)

#2 model data defilt django without rest
def no_rest_with_model(request):
    data = Guest.objects.all()
    response = {
        "guests": list(data.values("name", "mobile"))
    }
    return JsonResponse(response)


# List == GET
# Create == POST
# pk query == GET
# Update == PUT
# Delete destroy == DELETE

# 3 Function Based views
# 3.1 GET POST

@api_view(['GET', 'POST'])
def FBV_list(request): #FBV --> Function Based View

    # GET
    if request.method == 'GET':
        gests = Guest.objects.all()
        serializer = GuestSerializer(gests, many=True)
        return Response(serializer.data)

    # POST
    elif request.method == 'POST':
        serializer = GuestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)


# 3.2 GET PUT DELETE
@api_view(['GET', 'PUT', 'DELETE'])
def FBV_pk(request, pk):
    try:
        guest = Guest.objects.get(pk=pk)
    except Guest.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

     # GET
    if request.method == 'GET':
        serializer = GuestSerializer(guest)
        return Response(serializer.data)

     # PUT
    if request.method == 'PUT':
        serializer = GuestSerializer(guest, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


     # DELETE
    if request.method == 'DELETE':
        guest.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Class Based View (CBV)
#4.1 List and Create == GET POST
class CBV_list(APIView):
    def get(self, request):
        guests = Guest.objects.all()
        serializer = GuestSerializer(guests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = GuestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#4.2 GET PUT DELETE Class based view --> pk
class CBV_pk(APIView):

    def get_object(self, pk):
        try:
            return Guest.objects.get(pk=pk)
        except Guest.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        guest = self.get_object(pk)
        serializer = GuestSerializer(guest)
        return Response(serializer.data)

    def put(self, request, pk):
        guest = self.get_object(pk)
        serializer = GuestSerializer(guest, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        guest = self.get_object(pk)
        guest.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


#5 Mixins
#5.1 Mixins list
class Mixins_list(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  generics.GenericAPIView):

    queryset = Guest.objects.all()
    serializer_class = GuestSerializer

    def get(self, request):
        return self.list(request)

    def post(self, request):
        return self.create(request)

#5.2 Mixins get put delete --> pk
class Mixins_pk(mixins.RetrieveModelMixin, 
                mixins.UpdateModelMixin, 
                mixins.DestroyModelMixin, 
                generics.GenericAPIView):
    
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer

    def get(self, request, pk):
        return self.retrieve(request)

    def put(self, request, pk):
        return self.put(request)

    def delete(self, request, pk):
        return self.destroy(request)
    

#6 Generics
#6.1 GET POST
class Generics_list(generics.ListCreateAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    authentication_classes = [TokenAuthentication] 
    # permission_classes = [IsAuthenticated] # that person is allowed

#6.2 GET PUT DELETE --> pk
class Generics_pk(generics.RetrieveUpdateDestroyAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    authentication_classes = [TokenAuthentication] 
    # permission_classes = [IsAuthenticated] # that person is allowed


#7 viewsets
class viewsets_guest(viewsets.ModelViewSet):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer

class viewsets_movies(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['movie']

class viewsets_reservations(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ResevationSerializer


#8 Find Movie
@api_view(['GET'])
def find_movie(request):
    movies = Movie.objects.filter(hall = request.data['hall'] ,movie = request.data['movie'])
    serializer = MovieSerializer(movies, many=True)
    return Response(serializer.data)

#9 New reservation
@api_view(['POST'])
def New_reservation(request):
    movie = Movie.objects.get(hall = request.data['hall'] ,movie = request.data['movie'])
    guest = Guest()
    guest.name = request.data['name']
    guest.mobile = request.data['mobile']
    guest.save()

    reservation = Reservation()
    reservation.movie = movie
    reservation.guest = guest
    reservation.save()

    return Response(status=status.HTTP_201_CREATED)

#10 Post author editor
class Post_pk(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsauthorOrReadOnly]
    queryset = Post.objects.all()
    serializer_class = PostSerializer

