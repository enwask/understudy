from pandas import DataFrame
from understudy.api.rmp.course import CourseMetaSet
from understudy.api.rmp.professor import Professor
from understudy.api.rmp.rating import RatingSet

__all__ = ['Section']


class Section:
    """
    Represents an option of a professor teaching a course, with associated
    ratings and metadata for comparison.
    """

    def __init__(
        self,
        *,
        course: str,
        professor: Professor,
        ratings: RatingSet,
    ):
        self.course = course
        self.professor = professor

        self.num_ratings = len(ratings)
        self.ratings = ratings

        # Accumulate metadata from ratings
        self.meta = CourseMetaSet()
        for rating in ratings:
            self.meta += rating.meta

    @property
    def frame(self) -> DataFrame:
        return self.ratings.frame

    @property
    def quality(self) -> float:
        return self.ratings.quality

    @property
    def difficulty(self) -> float:
        return self.ratings.difficulty
