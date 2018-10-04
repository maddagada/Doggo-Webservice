#from django.shortcuts import render

# Create your views here.
from django.contrib.auth.models import *
from django.contrib.auth import *
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
#from django.shortcuts import render_to_response
from django.template import RequestContext
from django_filters.rest_framework import DjangoFilterBackend


from django.shortcuts import *

# Import models
from django.db import models
from django.contrib.auth.models import *
from api.models import *

#REST API
from rest_framework import viewsets, filters, parsers, renderers
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import *
from rest_framework.decorators import *
from rest_framework.authentication import *

#filters
#from filters.mixins import *

from api.pagination import *
import json, datetime, pytz
from django.core import serializers
import requests


def home(request):
   """
   Send requests to / to the ember.js clientside app
   """
   return render_to_response('ember/index.html',
               {}, RequestContext(request))

def xss_example(request):
  """
  Send requests to xss-example/ to the insecure client app
  """
  return render_to_response('dumb-test-app/index.html',
              {}, RequestContext(request))

class Register(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        # Login
        username = request.POST.get('username') #you need to apply validators to these
        print username
        password = request.POST.get('password') #you need to apply validators to these
        email = request.POST.get('email') #you need to apply validators to these
        gender = request.POST.get('gender') #you need to apply validators to these
        age = request.POST.get('age') #you need to apply validators to these
        educationlevel = request.POST.get('educationlevel') #you need to apply validators to these
        city = request.POST.get('city') #you need to apply validators to these
        state = request.POST.get('state') #you need to apply validators to these

        print request.POST.get('username')
        if User.objects.filter(username=username).exists():
            return Response({'username': 'Username is taken.', 'status': 'error'})
        elif User.objects.filter(email=email).exists():
            return Response({'email': 'Email is taken.', 'status': 'error'})

        #especially before you pass them in here
        newuser = User.objects.create_user(email=email, username=username, password=password)
        newprofile = Profile(user=newuser, gender=gender, age=age, educationlevel=educationlevel, city=city, state=state)
        newprofile.save()

        return Response({'status': 'success', 'userid': newuser.id, 'profile': newprofile.id})

class Session(APIView):
    permission_classes = (AllowAny,)
    def form_response(self, isauthenticated, userid, username, error=""):
        data = {
            'isauthenticated': isauthenticated,
            'userid': userid,
            'username': username
        }
        if error:
            data['message'] = error

        return Response(data)

    def get(self, request, *args, **kwargs):
        # Get the current user
        if request.user.is_authenticated():
            return self.form_response(True, request.user.id, request.user.username)
        return self.form_response(False, None, None)

    def post(self, request, *args, **kwargs):
        # Login
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return self.form_response(True, user.id, user.username)
            return self.form_response(False, None, None, "Account is suspended")
        return self.form_response(False, None, None, "Invalid username or password")

    def delete(self, request, *args, **kwargs):
        # Logout
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)

class Events(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (parsers.JSONParser,parsers.FormParser)
    renderer_classes = (renderers.JSONRenderer, )

    def get(self, request, format=None):
        events = Event.objects.all()
        json_data = serializers.serialize('json', events)
        content = {'events': json_data}
        return HttpResponse(json_data, content_type='json')

    def post(self, request, *args, **kwargs):
        print 'REQUEST DATA'
        print str(request.data)

        eventtype = request.data.get('eventtype')
        timestamp = int(request.data.get('timestamp'))
        userid = request.data.get('userid')
        requestor = request.META['REMOTE_ADDR']

        newEvent = Event(
            eventtype=eventtype,
            timestamp=datetime.datetime.fromtimestamp(timestamp/1000, pytz.utc),
            userid=userid,
            requestor=requestor
        )

        try:
            newEvent.clean_fields()
        except ValidationError as e:
            print e
            return Response({'success':False, 'error':e}, status=status.HTTP_400_BAD_REQUEST)

        newEvent.save()
        print 'New Event Logged from: ' + requestor
        return Response({'success': True}, status=status.HTTP_200_OK)

class ActivateIFTTT(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (parsers.JSONParser,parsers.FormParser)
    renderer_classes = (renderers.JSONRenderer, )

    def post(self,request):
        print 'REQUEST DATA'
        print str(request.data)

        eventtype = request.data.get('eventtype')
        timestamp = int(request.data.get('timestamp'))
        requestor = request.META['REMOTE_ADDR']
        api_key = ApiKey.objects.all().first()
        event_hook = "test"

        print "Creating New event"

        newEvent = Event(
            eventtype=eventtype,
            timestamp=datetime.datetime.fromtimestamp(timestamp/1000, pytz.utc),
            userid=str(api_key.owner),
            requestor=requestor
        )

        print newEvent
        print "Sending Device Event to IFTTT hook: " + str(event_hook)

        #send the new event to IFTTT and print the result
        event_req = requests.post('https://maker.ifttt.com/trigger/'+str(event_hook)+'/with/key/'+api_key.key, data= {
            'value1' : timestamp,
            'value2':  "\""+str(eventtype)+"\"",
            'value3' : "\""+str(requestor)+"\""
        })
        print event_req.text

        #check that the event is safe to store in the databse
        try:
            newEvent.clean_fields()
        except ValidationError as e:
            print e
            return Response({'success':False, 'error':e}, status=status.HTTP_400_BAD_REQUEST)

        #log the event in the DB
        newEvent.save()
        print 'New Event Logged'
        return Response({'success': True}, status=status.HTTP_200_OK)
class Dogs(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (parsers.JSONParser,parsers.FormParser)
    renderer_classes = (renderers.JSONRenderer, )

    def get_object(self, pk):
        try:
            return Breed.objects.get(pk=pk)
        except Breed.DoesNotExist:
            raise Http404

    def get(self, request, format=None):
        dogs = Dog.objects.all()
        json_data = serializers.serialize('json', dogs)
        content = {'dogs': json_data}
        return HttpResponse(json_data, content_type='json')

    def post(self, request, *args, **kwargs):
        print 'REQUEST DATA'
        print str(request.data)

        name = request.data.get('name')
        age = int(request.data.get('age'))
        breed = self.get_object(request.data.get('breed'))
        gender = request.data.get('gender')
        color = request.data.get('color')
        favoritefood = request.data.get('favoritefood')
        favoritetoy = request.data.get('favoritetoy')

        newDog = Dog(
            name = name,
            age = age,
            breed = breed,
            gender = gender,
            color = color,
            favoritefood = favoritefood,
            favoritetoy = favoritetoy,
        )

        try:
            newDog.clean_fields()
        except ValidationError as e:
            print e
            return Response({'success':False, 'error':e}, status=status.HTTP_400_BAD_REQUEST)

        newDog.save()
        print 'New Dog Logged from: '
        return Response({'success': True}, status=status.HTTP_200_OK)
class DogDetail(APIView):
    """
    Retrieve, update or delete a snippet instance.
    """

    def get_breed_object(self, pk):
        try:
            return Breed.objects.get(pk=pk)
        except Breed.DoesNotExist:
            raise Http404

    def get_object(self, pk):
        try:
            return Dog.objects.get(pk=pk)
        except Dog.DoesNotExist:
            raise Http404

    def get(self, request, id, format=None):

        dog = self.get_object(id)
        serializer = serializers.serialize('json', [dog])
        struct = json.loads(serializer)
        data = json.dumps(struct[0])
        return HttpResponse(data, content_type='json')

    def put(self, request, id, format=None):
        dog = self.get_object(id)

        dog.name = request.data.get('name')
        dog.age = int(request.data.get('age'))
        dog.breed = self.get_breed_object(request.data.get('breed'))
        dog.gender = request.data.get('gender')
        dog.color = request.data.get('color')
        dog.favoritefood = request.data.get('favoritefood')
        dog.favoritetoy = request.data.get('favoritetoy')

        dog.save()
        return Response({'success': True}, status=status.HTTP_200_OK)

    def delete(self, request, id, format=None):
        dog = self.get_object(id)
        dog.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class Breeds(APIView):
    permission_classes = (AllowAny,)
    parser_classes = (parsers.JSONParser,parsers.FormParser)
    renderer_classes = (renderers.JSONRenderer, )

    def get(self, request, format=None):
        breeds = Breed.objects.all()
        json_data = serializers.serialize('json', breeds)
        content = {'breed': json_data}
        return HttpResponse(json_data, content_type='json')

    def post(self, request, *args, **kwargs):
        print 'REQUEST DATA'
        print str(request.data)

        name = request.data.get('name')
        size = request.data.get('size')
        friendliness = request.data.get('friendliness')
        trainability = request.data.get('trainability')
        sheddingamount = request.data.get('sheddingamount')
        exerciseneeds = request.data.get('exerciseneeds')

        newBreed = Breed(
            name = name,
            size = size,
            friendliness = friendliness,
            trainability = trainability,
            sheddingamount = sheddingamount,
            exerciseneeds = exerciseneeds
        )

        try:
            newBreed.clean_fields()
        except ValidationError as e:
            print e
            return Response({'success':False, 'error':e}, status=status.HTTP_400_BAD_REQUEST)

        newBreed.save()
        print 'New Breed Logged from: '
        return Response({'success': True}, status=status.HTTP_200_OK)

class BreedDetail(APIView):
    """
    Retrieve, update or delete a snippet instance.
    """

    def get_object(self, pk):
        try:
            return Breed.objects.get(pk=pk)
        except Breed.DoesNotExist:
            raise Http404

    def get(self, request, id, format=None):

        breed = self.get_object(id)
        serializer = serializers.serialize('json', [breed])
        struct = json.loads(serializer)
        data = json.dumps(struct[0])
        return HttpResponse(data, content_type='json')

    def put(self, request, id, format=None):
        breed = self.get_object(id)

        breed.name = request.data.get('name')
        breed.size = request.data.get('size')
        breed.friendliness = request.data.get('friendliness')
        breed.trainability = request.data.get('trainability')
        breed.sheddingamount = request.data.get('sheddingamount')
        breed.exerciseneeds = request.data.get('exerciseneeds')

        breed.save()
        return Response({'success': True}, status=status.HTTP_200_OK)

    def delete(self, request, id, format=None):
        breed = self.get_object(id)
        breed.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
