from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task
def expand_question_iospec(question_pk):
    """
    Expand question's the IoSpec from template using the given model.

    After expansion is complete, sets the .is_valid attribute to True.
    """
    from ejudge_server.question_io.models import IoQuestion

    question = IoQuestion.objects.get(pk=question_pk)
    question.expand_inplace()


@shared_task
def autograde_submission(submission_pk):
    """
    Grade submission.
    """
    from ejudge_server.question_io.models import IoSubmission

    submission = IoSubmission.objects.get(pk=submission_pk)
    submission.feedback_auto()
