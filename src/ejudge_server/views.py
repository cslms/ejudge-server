from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(['GET'])
def root_view(request, format=None):
    return Response({
        'io-question-list': reverse('io:question-list', request=request, format=format),
        'io-grader-list': reverse('io:grader-list', request=request, format=format),

    })


@login_required
def profile_view(request):
    return render(request, 'profile.html', {'user': request.user})