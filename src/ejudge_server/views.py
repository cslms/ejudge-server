from rest_framework.routers import APIRootView
from rest_framework.schemas import get_schema_view

schema_view = get_schema_view(title='Ejudge server')
api_root_view = APIRootView.as_view(api_root_dict={
    'io': 'io-api-root',
    'code': 'code:api-root',
})


class IndexView(APIRootView):
    """
    Index page.
    """


index_view = IndexView.as_view(api_root_dict={
    'api': 'api-root',
    'schema': 'schema',
    'login': 'auth:login',
})
