import os

__all__ = ['count_teachers']


# Absolute root path for GraphQL queries
_query_root: str = os.path.join(
    os.path.dirname(__file__),
    '../../static/queries',
)


def _load_query(filename: str) -> str:
    """
    Loads a GraphQL query from a file.
    """

    path = os.path.join(_query_root, filename)
    with open(path, 'r') as f:
        return f.read()


count_teachers = _load_query('count_teachers.gql')
get_teachers = _load_query('get_teachers.gql')
get_ratings = _load_query('get_ratings.gql')
