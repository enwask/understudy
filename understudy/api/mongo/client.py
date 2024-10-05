import streamlit as st
from st_mongo_connection import MongoDBConnection

__all__ = ['db']


class db:
    professors = st.connection(
        'mongodb',
        collection='professors',
        type=MongoDBConnection,
    )

    professors_by_course = st.connection(
        'mongodb',
        collection='professors_by_course',
        type=MongoDBConnection,
    )

    ratings_by_professor = st.connection(
        'mongodb',
        collection='ratings_by_professor',
        type=MongoDBConnection,
    )
