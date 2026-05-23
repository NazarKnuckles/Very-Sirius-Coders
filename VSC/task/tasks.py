from celery import shared_task
from .sandbox import run_test_cases
from .models import Submission, SubmissionStatus


@shared_task
def execute_code_task(submission_id: int):
    submission = Submission.objects.get(id=submission_id)
    test_cases = submission.task.test_cases.all()
    results = run_test_cases(submission.code, test_cases)

    passed = sum(1 for r in results if r['passed'])
    total = len(results)
    status_name = 'Accepted' if passed == total else 'Wrong Answer'
    status, _ = SubmissionStatus.objects.get_or_create(name=status_name)

    submission.status = status
    submission.execution_time_ms = max((r['execution_time_ms'] for r in results), default=0)
    submission.save()

    return {'passed': passed, 'total': total}
