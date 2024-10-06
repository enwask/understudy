__all__ = ['CourseMeta', 'CourseMetaSet']


# TODO: get course name by code (scrape UCF catalog?)


class CourseMeta:
    """
    Describes course metadata that can be supplied in an RMP rating.
    Metadata values are optional and may be omitted.
    """

    def __init__(
        self,
        *,
        online: bool | None = None,
        attendance_required: bool | None = None,
        textbook_required: bool | None = None,
        tags: set[str] = set(),
    ):
        self.online = online
        self.attendance_required = attendance_required
        self.textbook_required = textbook_required
        self.tags = tags

    def to_dict(self) -> dict:
        """
        Converts data to a dictionary for serialization.
        """

        return {
            'online': self.online,
            'attendance_required': self.attendance_required,
            'textbook_required': self.textbook_required,
            'tags': list(self.tags),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CourseMeta':
        """
        Creates an instance from a dictionary.
        """

        return cls(
            online=data['online'],
            attendance_required=data['attendance_required'],
            textbook_required=data['textbook_required'],
            tags=set(data['tags']),
        )


class CourseMetaSet:
    """
    Accumulated course metadata from a given professor's section ratings.
    """

    def __init__(self):
        # Number of meta samples
        self.size: int = 0

        # Counters for metadata values
        self.online: tuple[int, int] = (0, 0)  # (false, true)
        self.attendance_required: tuple[int, int] = (0, 0)
        self.textbook_required: tuple[int, int] = (0, 0)
        self.tags: dict[str, int] = {}

    def __iadd__(self, meta: CourseMeta) -> 'CourseMetaSet':
        """
        Adds metadata to the accumulator.
        """

        # Online
        if meta.online is not None:
            tmp = list(self.online)
            tmp[meta.online] += 1
            self.online = tuple(tmp)

        # Attendance required
        if meta.attendance_required is not None:
            tmp = list(self.attendance_required)
            tmp[meta.attendance_required] += 1
            self.attendance_required = tuple(tmp)

        # Textbook required
        if meta.textbook_required is not None:
            tmp = list(self.textbook_required)
            tmp[meta.textbook_required] += 1
            self.textbook_required = tuple(tmp)

        # Tags
        for tag in meta.tags:
            self.tags[tag] = self.tags.get(tag, 0) + 1

        # Increment sample size
        self.size += 1

        return self


    def is_online(self) -> tuple[bool | None, float]:
        """
        Returns the most common online status and its frequency (0-100).
        """

        if self.size == 0:
            return None, 0

        return (
            self.online[1] > self.online[0],
            self.online[1] / self.size * 100
        )

    def requires_attendance(self) -> tuple[bool | None, float]:
        """
        Returns the most common attendance requirement response
        (mandated/not mandated/unknown) and its frequency (0-100).
        """

        if self.size == 0:
            return None, 0

        return (
            self.attendance_required[1] > self.attendance_required[0],
            self.attendance_required[1] / self.size * 100
        )

    def requires_textbook(self) -> tuple[bool | None, float]:
        """
        Returns the most common textbook requirement response
        (required/not required/unknown) and its frequency (0-100).
        """

        if self.size == 0:
            return None, 0

        return (
            self.textbook_required[1] > self.textbook_required[0],
            self.textbook_required[1] / self.size * 100
        )
