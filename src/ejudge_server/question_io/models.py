import json

from django.db import models
from django.utils.datetime_safe import datetime

import ejudge
import iospec


class HasIoSpecBase(models.Model):
    """
    Common functionality managing iospec data for both question and grader
    models.
    """

    class Meta:
        abstract = True

    iospec_pre = models.TextField(blank=True)
    iospec_post = models.TextField(blank=True)
    num_expansions = models.IntegerField(default=20)

    def get_tests(self, post_grade=False):
        """
        Return a parsed Iospec instance for the current tests.

        If post_grade=True, return tests for the post-grade evaluation phase.
        """
        return self.get_post_tests() if post_grade else self.get_pre_tests()

    def get_pre_tests(self):
        """
        Return an Iospec instance with all pre-tests.
        """

        spec = iospec.parse(self.iospec_pre)
        spec.expand_inputs(size=20)
        return spec

    def get_post_tests(self):
        """
        Return an Iospec instance with all post-tests.
        """

        if self.iospec_post:
            spec = iospec.parse(self.iospec_pre + '\n\n' + self.iospec_post)
        spec = iospec.parse(self.iospec_pre)
        spec.expand_inputs(size=20)
        return spec


class Question(HasIoSpecBase):
    """
    Represents a IO based question in the database.
    """

    name = models.CharField(max_length=100)
    question_id = models.IntegerField()
    source = models.TextField(blank=True)
    language = models.CharField(blank=True, max_length=50)

    def __str__(self):
        return '%s (%s)' % (self.name, self.language)

    def __repr__(self):
        return '<Question %r (%s)>' % (self.name, self.language)

    def new_grader(self, num_expansions):
        """
        Return a new grader for the question.
        """

        language = self.language
        pre_tests = self.get_pre_tests()
        post_tests = self.get_post_tests()
        source = self.source
        pre_tests_expansion = ejudge.run(source, pre_tests, lang=language)
        post_tests_expansion = ejudge.run(source, post_tests, lang=language)

        return Grader.objects.create(
            question=self,
            iospec_pre=pre_tests_expansion.source(),
            iospec_post=post_tests_expansion.source(),
        )

    def get_last_grader(self):
        """
        Return the current and most update grader instance.
        """

        return self.graders.last()


class Grader(HasIoSpecBase):
    """
    A grader object with expanded
    """

    class Meta:
        ordering = ['created']

    question = models.ForeignKey(Question, related_name='graders')
    created = models.DateTimeField(auto_created=True)
    usable = models.BooleanField(default=bool)

    @property
    def index(self):
        qs = (
            self.question.graders \
                .filter(created__lt=self.created)
        )
        return qs.count()

    def __str__(self):
        return '%s (%s-%s)' % (
        self.question.name, self.question.language, self.index)

    def __repr__(self):
        return '<Grader %r (%s-%s)>' % (
        self.question.name, self.question.language, self.index)

    def grade(self, source, language, post_grade=False):
        """
        Return a Feedback object for the given source.

        Args:
            source (str): Source code to be graded.
            language (str): Programming language of input source code.
            post_grade (bool): If True, uses the post-grading tests.
        """

        spec = self.get_tests(post_grade=False)
        return ejudge.grade(source, spec, lang=language)

    def grade_delayed(self, source, language, post_grade=False):
        job = GradingJob.objects.create(grader=self,
                                        source=source,
                                        language=language,
                                        post_grade=bool(post_grade))
        job.run_background()
        return job


class GradingJob(models.Model):
    """
    Represents a ongoing grading job.
    """

    created = models.DateTimeField(auto_created=True, auto_now=True)
    finished = models.DateTimeField(blank=True, null=True)
    grader = models.ForeignKey(Grader)
    source = models.TextField()
    language = models.CharField(max_length=20)
    post_grade = models.BooleanField()
    concluded = models.BooleanField(default=bool)
    running = models.BooleanField(default=bool)
    result_data = models.TextField(default='{}')

    @property
    def result(self):
        try:
            return self._result
        except AttributeError:
            self._result = json.loads(self.result_data)
            return self._result

    @result.setter
    def result(self, value):
        self.result_data = json.dumps(value)
        self._result = value

    def __str__(self):
        return 'Job: %s' % self.grader

    def run(self):
        """
        Grade current submission and fill the 'result' field
        """

        # Mark as running task
        self.running = False
        self.save(update_fields=['running'])

        # Run task and save results
        try:
            feedback = self.grader.grade(self.source, self.language,
                                         self.post_grade)
            feedback.pprint()
            self.result = feedback.to_json()
            self.finished = datetime.now()
            self.concluded = True
        finally:
            self.running = False
            self.save()
        return feedback

    def run_background(self):
        """
        Run grading task in background.
        """

        if self.pk is None:
            self.save()

        if not self.finished and not self.running:
            from .tasks import grade_code

            grade_code.delay(self.pk)
