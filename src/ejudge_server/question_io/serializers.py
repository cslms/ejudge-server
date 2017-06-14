from rest_framework import serializers

from ejudge_server.utils import full_url
from .models import IoQuestion, IoSubmission


class IoQuestionSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serialize IoQuestion models.
    """

    resources = serializers.SerializerMethodField()

    class Meta:
        model = IoQuestion
        fields = ('url', 'title', 'language', 'iospec_template', 'iospec',
                  'source', 'num_expansions', 'resources', 'uuid')

    def get_resources(self, obj):
        base_url = full_url('api/io/questions/%s/' % obj.uuid)
        return {
            'iospec': base_url + 'iospec/'
        }


class IoQuestionExpansionSerializer(serializers.Serializer):
    """
    Serializer for the /io/questions/{id}/iospec/ endpoint.
    """

    num_expansions = serializers.IntegerField()


class IoSubmissionSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for IoSubmission objects.
    """

    resources = serializers.SerializerMethodField()
    grade = serializers.SerializerMethodField()

    class Meta:
        model = IoSubmission
        fields = ('url', 'question', 'source', 'language', 'grade',
                  'resources', 'uuid')

    def get_resources(self, obj):
        base_url = full_url('api/io/submissions/%s/' % obj.uuid)
        return {
            'feedback': base_url + 'feedback/'
        }

    def get_grade(self, obj):
        return obj.feedback.grade if obj.has_feedback else None


class IoSubmissionFeedbackSerializer(serializers.Serializer):
    """
    Serializer for the /io/submissions/{id}/feedback/ endpoint.
    """
