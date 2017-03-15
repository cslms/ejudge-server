from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from ..utils import get_request_args
from .models import Question, Grader, GradingJob
from .serializers import QuestionSerializer, GraderSerializer, GradingJobSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    """
    View set for Question models.
    """

    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @detail_route(['POST'])
    def new_grader(self, request, pk=None, *args, **kwargs):
        """
        Create grader for question.
        """

        question = self.get_object()
        num_expansions = request.POST.get('num_expansions', 20)
        grader = question.new_grader(num_expansions=num_expansions)
        request.method = 'GET'
        return view_grader(request, pk=grader.pk)

    @detail_route(['GET'])
    def current_grader(self, request, pk=None, *args, **kwargs):
        """
        Create grader for question.
        """

        question = self.get_object()
        grader = question.get_last_grader()
        return view_grader(request, pk=grader.pk)

    @detail_route(['GET'])
    def graders(self, request, pk=None, *args, **kwargs):
        """
        Create grader for question.
        """

        qs = Grader.objects.filter(question_id=pk)
        view = GraderViewSet.as_view({'get': 'list'}, queryset=qs)
        return view(request)


class GraderViewSet(viewsets.ModelViewSet):
    """
    View set for Grader models.
    """

    queryset = Grader.objects.all()
    serializer_class = GraderSerializer

    @detail_route(['POST'])
    def grade_response(self, request, pk, source=None):
        """
        Grade response using given grader.
        """

        grader = get_object_or_404(Grader, pk=pk)

        source = request.POST.get('source', None)
        language = request.POST.get('language', None)
        post_grade = request.POST.get('post_grade', False)

        feedback = grader.grade(source, language, post_grade=post_grade)
        return Response(feedback.to_json())

    @detail_route(['POST'])
    def grade(self, request, pk=None, format=None):
        """
        Create a new grader
        """

        grader = self.get_object()
        kwargs = get_request_args(request, 'source', 'language', post_grade=True)
        source, language, post_grade = kwargs['source'], kwargs['language'], kwargs['post_grade']
        job = grader.grade_delayed(source, language, post_grade)
        job_serialized = GradingJobSerializer(job)
        return Response(job_serialized.data)

    def get_renderer_context(self):
        ctx = super().get_renderer_context()
        print(ctx)
        return ctx

view_grader = GraderViewSet.as_view({'get': 'retrieve'})


class GradingJobViewSet(viewsets.ModelViewSet):
    """
    View set for grading jobs.
    """

    queryset = GradingJob.objects.all()
    serializer_class = GradingJobSerializer

    @list_route()
    def pending(self, request, *args, **kwargs):
        queryset = self.queryset.filter(concluded=False)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    @list_route()
    def concluded(self, request, *args, **kwargs):
        queryset = self.queryset.filter(concluded=True)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)



