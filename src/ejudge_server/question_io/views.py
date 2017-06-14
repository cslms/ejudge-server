from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.routers import APIRootView

from .models import IoQuestion, IoSubmission
from .serializers import \
    IoQuestionSerializer, IoSubmissionSerializer, IoQuestionExpansionSerializer, \
    IoSubmissionFeedbackSerializer


# ------------------------------------------------------------------------------
# Questions
#
class QuestionIoViewSet(viewsets.ModelViewSet):
    """
    A programming question based on matching IO with a template.

    Performs a CRUD with default REST actions.

    The /api/io/questions/{id}/iospec/ resource represents the set of examples
    used to grade submissions to the current question.
    """

    queryset = IoQuestion.objects.all()
    serializer_class = IoQuestionSerializer


class QuestionExpansionViewSet(viewsets.ModelViewSet):
    """
    GET - return the status of the iospec expansion
    PUT - forces iospec expansion to happen
    """

    queryset = IoQuestion.objects.all()
    serializer_class = IoQuestionExpansionSerializer

    def retrieve_data(self, obj):
        return {
            'is_valid': obj.is_valid,
            'iospec': obj.iospec,
        }

    def retrieve(self, request, *args, **kwargs):
        return Response(self.retrieve_data(self.get_object()))

    def update(self, request, pk=None):
        obj = self.get_object()
        num_expansions = \
            request.data.get('num_expansions') or obj.num_expansions

        if not obj.is_valid or obj.num_expansions != num_expansions:
            obj.expand_inplace()

        return self.retrieve_data(obj)


# ------------------------------------------------------------------------------
# Submissions
#
class SubmissionIoViewSet(viewsets.ModelViewSet):
    """
    A submission of a program to an IO-based question.

    Performs a CRUD with default REST actions.

    The /api/io/submissions/{id}/feedback/ resource represents an automatically
    graded feedback to the submission.
    """

    queryset = IoSubmission.objects.all()
    serializer_class = IoSubmissionSerializer


class SubmissionFeedbackViewSet(viewsets.ModelViewSet):
    """
    Information about the feedback of a submission.

    GET - retrieves information of the feedback
    PUT - forces feedback to be calculated.
    """

    queryset = IoSubmission.objects.all()
    serializer_class = IoSubmissionFeedbackSerializer

    def retrieve_data(self, instance):
        if instance.has_feedback:
            grade = instance.feedback.grade
            feedback_data = instance.feedback.feedback_data
        else:
            grade = feedback_data = None

        return {
            'has_feedback': instance.has_feedback,
            'grade': grade,
            'feedback_data': feedback_data,
        }

    def retrieve(self, request, *args, **kwargs):
        return Response(self.retrieve_data(self.get_object()))

    def update(self, request, pk=None):
        instance = self.get_object()
        if not instance.has_feedback:
            instance.feedback_auto()
        return self.retrieve_data(instance)


# ------------------------------------------------------------------------------
# Root view: Personalizes APIRootView changing its name to "Io Root"
#
class IoView(APIRootView):
    """
    Basic resources for IO-based questions.

    /api/io/questions/: fetch and register new questions.
    /api/io/submissions/: submit response to questions.
    """


# ------------------------------------------------------------------------------
# View functions
#
question_iospec_view = QuestionExpansionViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
})
submission_feedback_view = SubmissionFeedbackViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
})
