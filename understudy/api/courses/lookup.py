import json
from understudy.api.courses.section import Section
from understudy.api.mongo.client import db
from understudy.api.rmp.professor import Professor
from understudy.api.rmp.rating import Rating, RatingSet

__all__ = ['collect_sections']


def collect_sections(
    course: str,
    *,
    min_reviews: int = 3,  # Min number of reviews to consider a section
    min_quality: float = 0,  # Min average quality rating (0-5)
    max_difficulty: float = 5,  # Max average difficulty rating (0-5)
    min_take_again: float = 0,  # Min % who would take professor again (0-100)
) -> list[Section]:
    """
    Collects professor sections for a course that meet criteria
    for review count, quality, difficulty, etc.
    """

    professors = map(
        Professor.from_dict,
        db.professors.find({
            'courses': course,
            'take_again': {
                '$gte': min_take_again,
            },
        }),
    )

    # Filtered sections
    res: list[Section] = []
    for prof in professors:
        # Retrieve ratings for this professor's section
        ratings = map(
            Rating.from_query_result,
            db.ratings.find({
                'professor': prof.id,
                'course': course,
            }),
        )

        # Check if this section meets the filter criteria
        rating_set = RatingSet(ratings)
        if (
            rating_set.num < min_reviews
            or rating_set.quality < min_quality
            or rating_set.difficulty > max_difficulty
        ):
            continue

        # Do the thing
        res.append(Section(
            course=course,
            professor=prof,
            ratings=rating_set,
        ))

    return res
