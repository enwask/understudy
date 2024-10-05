import asyncio
import logging
import re
from typing import Any

from aiohttp import ClientSession

import understudy.api.rmp.queries as queries
from understudy.api.rmp.course import CourseMeta
from understudy.api.rmp.professor import Professor
from understudy.api.rmp.rating import Rating

__all__ = [
    'Result',
    'RMP',
    'count_professors',
    'get_professors',
    'get_ratings_by_course',
    'get_ratings',
]

_log = logging.getLogger(__name__)

# Constants for the RMP graphql endpoint
# For some reason we can just copy a token from the browser and it works lol
_RMP_ENDPOINT = "https://www.ratemyprofessors.com/graphql"
_RMP_TOKEN = 'dGVzdDp0ZXN0'
_SCHOOL_ID = "U2Nob29sLTEwODI="


class Result(dict):
    """
    Dictionary with more convenient nested access.
    """

    # Dot/attribute access (not nested; values aren't wrapped)
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __getitem__(self, key: str | Any) -> Any:
        value: Any
        if isinstance(key, str) and '.' in key:
            keys = key.split('.')
            value = self
            for k in keys:
                value = value[k]
        else:
            value = super().__getitem__(key)

        # Wrap nested dictionaries for chained access
        if isinstance(value, dict):
            return Result(value)

        return value

    def items(self):
        return [
            (k, Result(v)) if isinstance(v, dict) else (k, v)
            for k, v in super().items()
        ]


class RMP(ClientSession):
    """
    An aiohttp session with the appropriate headers for interacting
    asynchronously with the RMP graphql endpoint.
    """

    def __init__(self, *args, **kwargs):
        headers = kwargs.pop("headers", {})
        headers.update({'authorization': f'Basic {_RMP_TOKEN}'})
        super().__init__(*args, headers=headers, **kwargs)

    async def query(self, query_str: str, **variables: Any) -> Result:
        """
        Queries the RMP graphql endpoint.
        """

        payload = {'query': query_str, 'variables': variables}
        res = await self.post(_RMP_ENDPOINT, json=payload)
        return Result(await res.json())


async def count_professors(school_id: str = _SCHOOL_ID) -> int:
    async with RMP() as rmp:
        res = await rmp.query(
            queries.count_teachers,
            **{
                'query': {
                    'text': "",
                    'schoolID': school_id,
                    'fallback': True,
                },
            },
        )
        return res['data.result.teachers.resultCount']


async def get_professors(school_id: str = _SCHOOL_ID) -> dict[str, Professor]:
    """
    Gets all professors listed under the school ID.
    """

    # Number of professors listed under the school ID
    num = await count_professors(school_id)

    # Fetched professor nodes, keyed by ID
    nodes: dict[str, dict] = {}

    # Unfortunately we can only query 1000 professors at a time,
    # and can't start from an offset index (need a cursor ID) so
    # we have to do chunked queries sequentially :(
    _log.debug('Fetching %d professor nodes...', num)
    async with RMP() as rmp:
        # Get the cursor ID of the first professor
        cursor: str = (
            await rmp.query(
                queries.get_teachers,
                **{
                    'count': 1,
                    'cursor': None,
                    'query': {
                        'text': "",
                        'schoolID': school_id,
                        'fallback': True,
                    },
                },
            )
        )['data.result.teachers.pageInfo.endCursor']

        # Get professor nodes sequentially
        while len(nodes) < num:
            # print("Fetching chunk", _ + 1, "of", num_chunks, "...")
            res = await rmp.query(
                queries.get_teachers,
                **{
                    'count': 1_000,
                    'cursor': cursor,
                    'query': {
                        'text': "",
                        'schoolID': school_id,
                        'fallback': True,
                    },
                },
            )

            # Update cursor for next chunk
            cursor = res['data.result.teachers.pageInfo.endCursor']

            # Add professors to nodes
            for node in res['data.result.teachers.edges']:
                nodes[node['node']['id']] = node['node']

            _log.debug(
                "...fetched %d nodes (now %d)...",
                len(res['data.result.teachers.edges']),
                len(nodes),
            )
        _log.debug("Found %d nodes", len(nodes))

    # Professor objects keyed by ID
    professors: dict[str, Professor] = {}

    # Parse professor nodes
    _log.debug("Parsing professor nodes...")
    for id, node in nodes.items():
        # Get course codes that have the correct format
        # (we throw away reviews that specify an incorrect code)
        courses: set[str] = set()
        for course in node['courseCodes']:
            code: str = course['courseName']
            if code and re.match(r'^[A-Za-z]{3}\d{4}[A-Za-z]?$', code):
                # If there's an extra letter on the end (H or C), just drop it
                courses.add(code[:7].upper())

        # Create the professor instance
        professors[id] = Professor(
            id=id,
            name="%s %s" % (node['firstName'], node['lastName']),
            dept=node['department'],
            quality=node['avgRating'],
            difficulty=node['avgDifficulty'],
            take_again=node['wouldTakeAgainPercent'],
            courses=courses,
        )

    _log.debug("Retrieved %d professors", len(professors))
    return professors


async def get_ratings_by_course(
    professor_id: str,
    course: str,
) -> tuple[str, list[Rating]]:
    """
    Gets all of a professor's ratings for a given course.
    Returns (course, [Rating...])
    """

    # Rating nodes keyed by their ID
    nodes: dict[str, dict] = {}

    # Fetch ratings for this course, including combined and honors sections
    async with RMP() as rmp:
        for course_filter in (course, '%sH' % course, '%sC' % course):
            _log.debug("Fetching ratings for %s...", course_filter)
            res = await rmp.query(
                queries.get_ratings,
                **{
                    'id': professor_id,
                    'count': 1_000,
                    'courseFilter': course_filter,
                },
            )

            # Update node map
            for node in res['data.node.ratings.edges']:
                nodes[node['node']['id']] = node['node']

            _log.debug(
                "...fetched %d nodes (now %d)",
                len(res['data.node.ratings.edges']),
                len(nodes),
            )

    # Parsed ratings
    ratings: list[Rating] = []

    # Parse nodes into Rating objects
    _log.debug("Parsing rating nodes...")
    for id, node in nodes.items():
        # Process course metadata from the review
        meta = CourseMeta(
            online=node['isForOnlineClass'],
            attendance_required=(
                True
                if node['attendanceMandatory'] == "mandatory"
                else (
                    False
                    if node['attendanceMandatory'] == "non mandatory"
                    else None
                )
            ),
            textbook_required=(
                True
                if node['textbookUse'] == 1
                else (False if node['textbookUse'] == 0 else None)
            ),
            tags=set([tag.strip() for tag in node['ratingTags'].split('--') if tag]),
        )

        # Construct the actual rating object
        ratings.append(
            Rating(
                id=id,
                quality=node['helpfulRating'],
                difficulty=node['difficultyRating'],
                comment=node['comment'],
                grade=(None if node['grade'].isspace() else node['grade']),
                for_credit=node['isForCredit'],
                meta=meta,
                votes=(
                    node['thumbsUpTotal'],
                    node['thumbsDownTotal'],
                ),
            )
        )

    _log.debug("Parsed %d ratings", len(ratings))
    return course, ratings


async def get_ratings(
    professor_id: str,
    courses: set[str],
) -> tuple[str, dict[str, list[Rating]]]:
    """
    Gets all of a professor's ratings for each of the given courses.
    Returns (professor_id, { course: [Rating...] })
    """

    # Ratings keyed by course
    ratings: dict[str, list[Rating]] = {}

    # Fetch ratings for all courses in parallel
    _log.debug("Fetching ratings for %d courses...", len(courses))
    tasks = []
    for course in courses:
        tasks.append(asyncio.create_task(
            get_ratings_by_course(professor_id, course)))

    # Wait for all tasks to complete
    res: list[tuple[str, list[Rating]]] = await asyncio.gather(*tasks)
    for course, course_ratings in res:
        ratings[course] = course_ratings

    total_ratings = sum(len(r) for r in ratings.values())
    _log.debug("Fetched %d ratings for %d courses", total_ratings, len(ratings))
    return professor_id, ratings
