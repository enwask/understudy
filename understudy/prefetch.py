import asyncio
import logging

from understudy.api.mongo.client import db
from understudy.api.rmp.data import get_professors, get_ratings
from understudy.api.rmp.rating import Rating

logging.basicConfig(level=logging.DEBUG)


async def main() -> None:
    """
    Prefetches RMP data and loads it into the Mongo database.
    """

    # Fetch all professors
    professors = await get_professors()

    # Drop stale data and write professors to the Mongo database
    db.professors.delete({})
    db.professors.insert([
        prof.to_dict()
        for prof in professors.values()
    ])

    # Map of professor -> { course -> [Rating...] }
    prof_ratings: dict[str, dict[str, list[Rating]]] = {}

    # Fetch ratings for professors asynchronously
    # We do this in batches to avoid running out of memory
    batch_size = 10
    for start in range(0, len(professors), batch_size):
        tasks = []
        for id, prof in list(professors.items())[start:start + batch_size]:
            tasks.append(asyncio.create_task(get_ratings(id, prof.courses)))
        res = await asyncio.gather(*tasks)
        for id, ratings_by_course in res:
            prof_ratings[id] = ratings_by_course

        # Artificial throttling to avoid DNS issues
        await asyncio.sleep(0.1)

    # Drop old ratings data
    db.ratings.delete({})

    # Write ratings to the Mongo database
    for prof, ratings_by_course in prof_ratings.items():
        for course, ratings in ratings_by_course.items():
            if len(ratings) == 0:
                # Empty docs list fails for some reason
                continue

            db.ratings.insert([
                {
                    'professor': prof,
                    'course': course,
                    'rating': r.to_dict()
                }
                for r in ratings
            ])

if __name__ == "__main__":
    asyncio.run(main())
