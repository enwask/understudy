__all__ = ['Professor']


class Professor:
    """
    Describes a professor and associated classes/ratings information.
    """

    def __init__(
        self,
        *,
        id: str,
        name: str,
        dept: str,
        quality: float,  # avg quality 0-5
        difficulty: float,  # avg difficulty 0-5
        take_again: float,  # % would take again (0-100)
        courses: set[str] = set(),
    ):
        self.id = id
        self.name = name
        self.dept = dept
        self.quality = quality
        self.difficulty = difficulty
        self.take_again = take_again
        self.courses = courses

    def to_dict(self) -> dict:
        """
        Converts data to a dictionary for serialization.
        """

        return {
            'id': self.id,
            'name': self.name,
            'dept': self.dept,
            'quality': self.quality,
            'difficulty': self.difficulty,
            'take_again': self.take_again,
            'courses': list(self.courses),
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Professor':
        """
        Creates an instance from a dictionary.
        """

        return cls(
            id=data['id'],
            name=data['name'],
            dept=data['dept'],
            quality=data['quality'],
            difficulty=data['difficulty'],
            take_again=data['take_again'],
            courses=set(data['courses']),
        )

    def add_courses(self, *courses: str):
        """
        Adds a course this professor is known to teach.
        """

        self.courses.update(courses)

    def has_course(self, course: str) -> bool:
        """
        Checks if the professor is known to teach a course.
        """

        return course in self.courses
