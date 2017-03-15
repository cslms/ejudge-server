from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


# Mokey patch ejudge.execution_manager to use billiard.Process instead of
# multiprocessing.Process
import billiard
from ejudge import execution_manager as _ex
_ex.multiprocessing = billiard


@shared_task
def grade_code(job_pk):
    from .models import GradingJob

    job = GradingJob.objects.get(pk=job_pk)
    job.running = True
    job.save(update_fields=['running'])
    result = job.run()
    return result.to_json()