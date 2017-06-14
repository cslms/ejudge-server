import jsonfield
import logging
import uuid
from django.core import validators
from django.db import models

from .tasks import expand_question_iospec, autograde_submission
from .utils import iospec_expand, grade_submission

logger = logging.getLogger('question_io')

LANGUAGE_CHOICES = [
    ('python', 'Python 3.x'),
    ('python2', 'Python 2.7'),
    ('gcc', 'C (gcc 6.3 --std=c99)'),
]


class IoQuestion(models.Model):
    """
    Represents a IO based question in the database.
    """

    title = models.CharField(
        max_length=100,
        help_text=(
            'IoQuestion\'s name'
        )
    )
    uuid = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        help_text=(
            'Universal Unique Identifier.'
        )
    )
    source = models.TextField(
        help_text=(
            'Source code for the reference solution used to expand the '
            'iospec template.'
        )
    )
    language = models.CharField(
        max_length=50,
        choices=LANGUAGE_CHOICES,
        help_text=(
            'Programming language used in the reference program.'
        )
    )
    iospec = models.TextField(
        blank=True,
        editable=False,
        help_text=(
            'Expanded iospec data. Use the ./iospec-expansion/ endpoint in '
            'order to force/control expansion'
        )
    )

    iospec_template = models.TextField(
        help_text=(
            'Correction template written in the iospec format.'
        )
    )
    num_expansions = models.IntegerField(
        default=25,
        help_text=(
            'Default number of expansions computed from the iospec template.'
        )
    )
    is_valid = models.BooleanField(default=bool)

    def __str__(self):
        return '%s (%s)' % (self.title, self.uuid)

    def __repr__(self):
        return '<IoQuestion %r (%s)>' % (self.title, self.uuid)

    _iospec_expand = staticmethod(iospec_expand)

    def save(self, schedule=True, **kwargs):
        super().save(**kwargs)
        if schedule and not self.iospec:
            expand_question_iospec.delay(self.pk)

    def expand_inplace(self, commit=True):
        """
        Expands iospec template inplace saving results on the database.
        """

        logger.info('expanding question: %s' % self)
        from pprint import pprint
        pprint(self.__dict__)
        self.iospec = self._iospec_expand(
            self.iospec_template,
            self.source,
            self.language
        )
        self.is_valid = True
        pprint(self.__dict__)
        if commit:
            super().save()


class IoSubmission(models.Model):
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
        IoQuestion,
        related_name='submissions',
    )
    source = models.TextField(
        help_text=(
            'Source code for submission.'
        )
    )
    language = models.CharField(
        max_length=50,
        choices=LANGUAGE_CHOICES,
        help_text=(
            'Programming language used in the submitted program.'
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

    # It is here to helo mocking
    _grade_submission = staticmethod(grade_submission)

    def save(self, schedule=True, **kwargs):
        super().save(**kwargs)
        if schedule and not self.has_feedback:
            autograde_submission.delay(self.pk)

    def feedback_auto(self, commit=True):
        """
        Grade submission and return a IoFeedback instance.
        """

        logger.info('grading submission: %s (%s)' % (self, self.question))

        grade, feedback_data = self._grade_submission(
            self.question.iospec_template,
            self.source,
            self.language
        )
        feedback = IoFeedback(
            grade=grade, submission=self, feedback_data=feedback_data
        )
        self.has_feedback = True

        if commit:
            feedback.save()
            self.save(update_fields=['has_feedback'])
        return feedback


class IoFeedback(models.Model):
    """
    IoFeedback for submission.
    """

    submission = models.OneToOneField(
        IoSubmission,
        related_name='feedback',
        primary_key=True,
    )
    grade = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[
            validators.MinValueValidator(0),
            validators.MaxValueValidator(100),
        ])
    feedback_data = jsonfield.JSONField()
