from typing import Iterable

import pandas as pd
from understudy.api.rmp.course import CourseMeta

__all__ = ['Rating', 'RatingSet']


class Rating:
    """
    Describes a RateMyProfessor rating.
    """

    def __init__(
        self,
        *,
        id: str,
        quality: float,
        difficulty: float,
        comment: str,
        grade: str | None,
        for_credit: bool,
        meta: CourseMeta,
        votes: tuple[int, int],  # (helpful, unhelpful)
    ):
        self.id = id
        self.quality = quality
        self.difficulty = difficulty
        self.comment = comment
        self.grade = grade
        self.for_credit = for_credit
        self.meta = meta
        self.votes = votes

    def to_dict(self) -> dict:
        """
        Converts data to a dictionary for serialization.
        """

        return {
            'id': self.id,
            'quality': self.quality,
            'difficulty': self.difficulty,
            'comment': self.comment,
            'grade': self.grade,
            'for_credit': self.for_credit,
            'meta': self.meta.to_dict(),
            'votes': self.votes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Rating':
        """
        Creates an instance from a dictionary.
        """

        return cls(
            id=data['id'],
            quality=data['quality'],
            difficulty=data['difficulty'],
            comment=data['comment'],
            grade=data['grade'],
            for_credit=data['for_credit'],
            meta=CourseMeta.from_dict(data['meta']),
            votes=data['votes'],
        )
    
    @classmethod
    def from_query_result(cls, data: dict) -> 'Rating':
        """
        Creates an instance from a query result.
        """

        return cls.from_dict(data['rating'])


class RatingSet:
    """
    Describes a collection of ratings, as well as overall data
    inferred from them such as average quality/difficulty.

    Iterating iterates over the ratings.
    """

    def __init__(self, ratings: Iterable[Rating]):
        self.ratings = tuple(ratings)
        self.num = len(self.ratings)

        # Construct a dataframe from ratings
        self.frame = pd.DataFrame(
            [(r.quality, r.difficulty) for r in self.ratings],
            columns=['quality', 'difficulty'],
        )

        # Compute mean quality/difficulty
        self.quality = self.frame['quality'].mean()
        self.difficulty = self.frame['difficulty'].mean()

    def __iter__(self):
        return iter(self.ratings)

    def __len__(self):
        return self.num
