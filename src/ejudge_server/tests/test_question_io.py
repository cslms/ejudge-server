import mock
import pytest
from django.db.models import Model

from ejudge_server.question_io import tasks
from ejudge_server.question_io.models import IoQuestion, IoSubmission
from ejudge_server.question_io.serializers import IoQuestionSerializer, \
    IoSubmissionSerializer
from ejudge_server.question_io.tasks import expand_question_iospec, \
    autograde_submission
from ejudge_server.question_io.utils import iospec_expand, grade_submission
from ejudge_server.question_io.views import QuestionExpansionViewSet

patch_object = mock.patch.object


# ------------------------------------------------------------------------------
# MODELS
#
class TestIoQuestion:

    @pytest.fixture
    def uuid(self):
        return '411a5110-896d-4ec5-86bf-c8c381004189'

    @pytest.fixture
    def question(self, uuid):
        return IoQuestion(
            title='title',
            language='python',
            source='print("hello")',
            iospec_template='hello',
            uuid=uuid,
        )

    def test_create_io_question(self, question, uuid):
        question.full_clean(validate_unique=False)
        assert question.num_expansions == 25
        assert question.iospec == ''
        assert str(question.uuid) == uuid
        assert str(question) == "title (%s)" % uuid
        assert repr(question) == "<IoQuestion 'title' (%s)>" % uuid

    def test_expand_inplace(self, question):
        with patch_object(Model, 'save', lambda *args, **kwargs: None):
            with patch_object(IoQuestion,
                              '_iospec_expand',
                              staticmethod(lambda template, y, z: template)):
                question.expand_inplace()

        assert question.iospec == question.iospec_template

    def test_save_activate_task(self, question):
        saved = False
        scheduled = False

        def save(self, **kwargs):
            nonlocal saved

            saved = True

        def task(pk):
            nonlocal scheduled

            scheduled = True

        with patch_object(Model, 'save', save):
            with patch_object(expand_question_iospec, 'delay', task):
                question.save()

        assert saved
        assert scheduled


class TestIoSubmission:
    uuid = TestIoQuestion.uuid
    question = TestIoQuestion.question

    @pytest.fixture
    def sub_uuid(self):
        return '411a5110-896d-4ec5-86bf-c8c381004189'

    @pytest.fixture
    def submission(self, question, sub_uuid):
        return IoSubmission(uuid=sub_uuid,
                            question=question,
                            source='print("hello")',
                            language='python')

    def test_create_io_submission(self, submission, question, sub_uuid):
        submission.full_clean(validate_unique=False, exclude=['question'])
        assert str(submission.uuid) == sub_uuid
        assert str(submission) == '%s (title/python)' % sub_uuid
        assert repr(submission) == "<IoSubmission %s (title/python)>" % sub_uuid

    def test_expand_inplace(self, submission):
        with patch_object(Model, 'save', lambda *args, **kwargs: None):
            with patch_object(IoSubmission,
                              '_grade_submission',
                              staticmethod(lambda x, y, z: (100.0, {}))):
                fb = submission.feedback_auto()
        assert fb.grade == 100.0

    def test_save_activate_task(self, submission):
        saved = False
        scheduled = False

        def save(self, **kwargs):
            nonlocal saved

            saved = True

        def task(pk):
            nonlocal scheduled

            scheduled = True

        with patch_object(Model, 'save', save):
            with patch_object(autograde_submission, 'delay', task):
                submission.save()

        assert saved
        assert scheduled


# ------------------------------------------------------------------------------
# SERIALIZERS
#
class TestIoQuestionSerializer:
    question = TestIoQuestion.question
    uuid = TestIoQuestion.uuid

    def test_question_serializer(self, question, uuid):
        serializer = IoQuestionSerializer(question, context={'request': None})
        assert serializer.data == {
            'title': 'title',
            'iospec': '',
            'iospec_template': 'hello',
            'language': 'python',
            'num_expansions': 25,
            'resources': {
                'iospec': 'http://localhost:8000/api/io/questions/' + uuid +
                          '/iospec/'
            },
            'source': 'print("hello")',
            'url': '/api/io/questions/%s/' % uuid,
            'uuid': uuid,
        }


class TestIoSubmissionSerializer:
    question = TestIoQuestion.question
    submission = TestIoSubmission.submission
    uuid = TestIoQuestion.uuid
    sub_uuid = TestIoSubmission.sub_uuid

    def test_question_serializer(self, submission, sub_uuid, uuid):
        serializer = IoSubmissionSerializer(submission,
                                            context={'request': None})
        assert serializer.data == {
            'question': '/api/io/questions/%s/' % uuid,
            'language': 'python',
            'source': 'print("hello")',
            'grade': None,
            'resources': {
                'feedback': 'http://localhost:8000'
                            '/api/io/submissions/%s/feedback/' % sub_uuid
            },
            'url': '/api/io/submissions/%s/' % uuid,
            'uuid': sub_uuid,
        }


# ------------------------------------------------------------------------------
# UTILS
#
class TestUtils:

    def test_iospec_expand(self):
        iospec = '@input John'
        source = 'print(input("name"))'
        with mock.patch('ejudge_server.question_io.utils.SANDBOX', False):
            result = iospec_expand(iospec, source, 'python')
        assert result == 'name<John>\nJohn'

    def test_grade_submission(self):
        iospec = 'name<John>\nJohn'
        source = 'print(input("name"))'
        with mock.patch('ejudge_server.question_io.utils.SANDBOX', False):
            grade, feedback = grade_submission(iospec, source, 'python')
        assert feedback == {
            'grade': 1.0,
            'hint': None,
            'message': None,
            'status': 'ok',
            'answer_key': {
                'type': 'standard',
                'data': [['Out', 'name'], ['In', 'John'], ['Out', 'John']],
            },
            'testcase': {
                'type': 'standard',
                'data': [['Out', 'name'], ['In', 'John'], ['Out', 'John']],
            },
        }
        assert grade == 100


# ------------------------------------------------------------------------------
# TASKS
#
class TestTasks:
    question = TestIoQuestion.question
    uuid = TestIoQuestion.uuid
    submission = TestIoSubmission.submission
    sub_uuid = TestIoSubmission.sub_uuid

    def test_task_expand_question_iospec(self, db, question):
        question.save(schedule=False)
        with mock.patch('ejudge_server.question_io.utils.SANDBOX', False):
            tasks.expand_question_iospec(question.pk)
        question.refresh_from_db()
        assert question.iospec == 'hello'

    def test_autograde_submission(self, db, submission, question):
        question.save(schedule=False)
        submission.save(schedule=False)

        with mock.patch('ejudge_server.question_io.utils.SANDBOX', False):
            tasks.autograde_submission(submission.pk)
        submission.refresh_from_db()
        assert submission.has_feedback
        assert submission.feedback.grade == 100


# ------------------------------------------------------------------------------
# VIEWS
#
class TestExpansionViewSet:
    question = TestIoQuestion.question
    uuid = TestIoQuestion.uuid

    def test_question_iospec_retrieve(self, question, uuid, rf):
        request = rf.get('/api/io/questions/%s/iospec/' % uuid)
        viewset = QuestionExpansionViewSet(kwargs={'pk': uuid})

        with mock.patch('ejudge_server.question_io.views.Response', dict):
            with patch_object(
                    QuestionExpansionViewSet, 'get_object', lambda x: question):
                assert viewset.retrieve(request) == {
                    'iospec': '',
                    'is_valid': False,
                }

    def test_question_iospec_update(self, question, uuid, rf):
        request = rf.get('/api/io/questions/%s/iospec/' % uuid)
        request.data = {'num_expansions': 2}
        viewset = QuestionExpansionViewSet(kwargs={'pk': uuid})
        iospec = question.iospec_template

        patch_get_object = patch_object(
            QuestionExpansionViewSet, 'get_object', lambda x: question
        )
        patch_expand_inplace = patch_object(
            IoQuestion, 'expand_inplace', lambda x: setattr(
                x, 'iospec', iospec)
        )

        with patch_get_object, patch_expand_inplace:
            assert viewset.update(request) == {
                'iospec': 'hello',
                'is_valid': False,
            }
