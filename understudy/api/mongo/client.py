import streamlit as st
from st_mongo_connection import MongoDBConnection

__all__ = ['db']


class db:
    """
    MongoDB database connections.
    """

    professors = st.connection(
        'mongodb',
        collection='professors',
        type=MongoDBConnection,
    )

    ratings = st.connection(
        'mongodb',
        collection='ratings',
        type=MongoDBConnection,
    )
