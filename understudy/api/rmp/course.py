# Course code type
__all__ = ['CourseMeta']


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
