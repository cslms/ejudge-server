from rest_framework import serializers

from .models import Question, Grader, GradingJob


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'


class GraderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grader
        fields = '__all__'


class GradingJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradingJob
        fields = '__all__'

    created = serializers.DateTimeField(read_only=True)
    finished = serializers.DateTimeField(read_only=True)