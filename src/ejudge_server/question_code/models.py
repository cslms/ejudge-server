import logging
import uuid
from django.core import validators
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from .grader import get_code_errors
from .tasks import autograde_submission

logger = logging.getLogger('question_io')

LANGUAGE_CHOICES = [
    ('python', 'Python 3.x'),
    ('python2', 'Python 2.7'),
    ('gcc', 'C (gcc 6.3 --std=c99)'),
]


class CodeQuestion(models.Model):
    """
    Represents a IO based question in the database.


    Grade a question by comparing the student's implementation with a reference
    implementation and some examples.
    """

    title = models.CharField(
        max_length=100,
        help_text=(
            'Question\'s name'
        )
    )
    uuid = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        help_text=mark_safe(_(
            'Universal Unique Identifier.<br>\n'
            'This identifier must be the same both in the main Codeschool site '
            'and in the Ejudge microservice.'
        ))
    )

    grader = models.TextField(
        _('Grader source code'),
        help_text=_(
            'The grader is a Python script that defines a '
            '"grade(test, reference)" function that takes the test function '
            'and a reference implementation and raise AssertionErrors if '
            'something fail.'
        ),
    )
    reference = models.TextField(
        _('Reference implementation'),
        help_text=_(
            'Reference implementation for the correct function. This is an '
            'example of a correct implementation of the current question.'
        ),
    )
    function_name = models.CharField(
        _('Function name'),
        max_length=80,
        default='func',
        help_text=_(
            'The name of the test object. (This is normally a function, but '
            'we can also test classes, data structures, or anything)',
        ),
    )
    timeout = models.FloatField(
        _('Timeout'),
        default=1.0,
        help_text=_(
            'Maximum interval (in seconds) used to grade the question.'
        ),
    )
    is_valid = models.BooleanField(default=bool)

    def __str__(self):
        return '%s (%s)' % (self.title, self.uuid)

    def __repr__(self):
        return '<CodeQuestion %r (%s)>' % (self.title, self.uuid)


class CodeSubmission(models.Model):
    """
    An anonymous submission.

    The Codeschool main application should take care of assinging submissions
    to users. The only responsibility of the ejudge-server is to register
    questions and grade submissions.
    """

    uuid = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True
    )
    question = models.ForeignKey(
        CodeQuestion,
        related_name='submissions',
    )
    source = models.TextField(
        help_text=(
            'Source code for submission.'
        )
    )
    has_feedback = models.BooleanField(
        editable=False,
        default=bool,
    )

    def __str__(self):
        return '%s (%s/%s)' % (self.uuid, self.question.title, self.language)

    def __repr__(self):
        return '<IoSubmission %s (%s/%s)>' % (
            self.uuid, self.question.title, self.language
        )

    def save(self, schedule=True, **kwargs):
        super().save(**kwargs)
        if schedule and not self.has_feedback:
            autograde_submission.delay(self.pk)

    def feedback_auto(self, commit=True):
        """
        Grade submission and return a CodeFeedback instance.
        """

        get_code_errors(...)
        logger.info('grading submission: %s (%s)' % (self, self.question))

        grade, feedback_data = self._grade_submission(
            self.question.iospec_template,
            self.source,
            self.language
        )
        feedback = CodeFeedback(
            grade=grade, submission=self, feedback_data=feedback_data
        )
        self.has_feedback = True

        if commit:
            feedback.save()
            self.save(update_fields=['has_feedback'])
        return feedback


class CodeFeedback(models.Model):
    """
    IoFeedback for submission.
    """

    submission = models.OneToOneField(
        CodeSubmission,
        related_name='feedback',
        primary_key=True,
    )
    grade = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[
            validators.MinValueValidator(0),
            validators.MaxValueValidator(100),
        ])
    error_message = models.TextField(blank=True)

    def get_autograde_value(self):
        question = self.question
        submission = self.submission

        source = submission.source
        error = find_code_errors(question, source)
        return 100 if error is None else 0, {'error_message': error or ''}


def find_code_errors(question, code, use_sandbox=True):
    """
    Return an error message for any defects encountered on the given string
    of python code.
    """

    args = (question.grader, code, question.reference, question.function_name)
    runner = lambda f, args, **kwargs: f(*args)

    if use_sandbox:
        import boxed

        runner = boxed.run

    return \
        runner(code_errors,
               args=args,
               serializer='json',
               timeout=question.timeout,
               imports=['ejudge_server.question_code.grader'])
