from understudy.api.rmp.course import CourseMeta


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
