import os
import pandas as pd
import plotly.express as px
import streamlit as st

from understudy.api.courses.lookup import collect_courses, collect_sections


# Min thresholds for displaying tags/courses
_TAG_THRESHOLD = 10
_COURSE_THRESHOLD = 10


# Hacky styling
_static_root: str = os.path.join(os.path.dirname(__file__), 'static')
with open(os.path.join(_static_root, 'styles.css'), 'r') as f:
    st.markdown("<style>%s</style>" % f.read(), unsafe_allow_html=True)


# Main title
st.title("understudy", anchor=False)
st.header("choose professors, wisely.", anchor=False)
st.divider()

# Course code selection
course = st.selectbox(
    "Select a course:",
    options=collect_courses(min_occurences=_COURSE_THRESHOLD),
    index=None,
    placeholder="Enter a course code...",
)
if not course:
    st.stop()


# Search / filter container
with st.expander(
    "Filter options",
):
    st.write(
        "<span id='filter-marker'></span>",
        unsafe_allow_html=True,
    )

    # Filter options
    cols = st.columns(4)
    min_reviews = cols[0].number_input(
        "Min review count",
        min_value=3,
        max_value=100,
        step=1,
    )
    min_quality = cols[1].number_input(
        "Min average quality",
        value=3.0,
        min_value=0.0,
        max_value=5.0,
        step=0.5,
    )
    max_difficulty = cols[2].number_input(
        "Max average difficulty",
        value=5.0,
        min_value=0.0,
        max_value=5.0,
        step=0.5,
    )
    min_take_again = cols[3].number_input(
        "Min % recommend",
        value=50,
        min_value=0,
        max_value=100,
        step=5,
    )

    # Collect sections for the selected course
    sections = collect_sections(
        course=course,
        min_reviews=min_reviews,
        min_quality=min_quality,
        max_difficulty=max_difficulty,
        min_take_again=min_take_again,
    )

    # Find set of all tags any section has
    tags_dict: dict[str, int] = {}
    for section in sections:
        for tag, num in section.meta.tags.items():
            tags_dict[tag] = tags_dict.get(tag, 0) + num
    tags = sorted([tag for tag, num in tags_dict.items()
                   if num >= _TAG_THRESHOLD])

    # Filter sections by tags
    tag_filter = st.multiselect(
        "Filter by tags:",
        tags,
    )


# Render search results
st.divider()
st.header("Matching course sections", anchor=False)
matches = 0
for section in sections:
    # Filter by the selected tags
    if not all(tag in section.meta.tags for tag in tag_filter):
        continue
    matches += 1

    # Create a box plot for quality and difficulty
    frame = pd.DataFrame(
        [(r.quality, 'quality') for r in section.ratings] +
        [(r.difficulty, 'difficulty') for r in section.ratings],
        columns=['value', 'type'],
    )
    fig = px.box(
        frame,
        x='value',
        y='type',
        color='type',
        height=150,
    )
    fig.update_traces(orientation='h')
    fig.update_layout(
        hovermode=False,
        showlegend=False,
        xaxis={
            'title': '',
            'fixedrange': True,
            'tickfont': dict(size=16),
        },
        yaxis={
            'title': '',
            'fixedrange': True,
            'tickfont': dict(size=16),
            'side': 'right',
        },
        margin=dict(t=0, b=0, l=0, r=0),
        font=dict(size=16),
    )

    with st.expander(
        section.professor.name,
        expanded=True,
    ):
        # Display tags for this section
        wtags = [
            "<span class='tag-badge'>%s</span>" % tag
            for tag, num in section.meta.tags.items()
            if num >= _TAG_THRESHOLD or tag in tag_filter
        ]
        if len(wtags) > 0:
            st.write(
                ''.join(wtags),
                unsafe_allow_html=True,
            )
            st.divider()

        # Display section metadata
        l, r = st.columns([1, 2])
        l.write("Mean quality rating: **%.2f**" % section.quality)
        r.progress(section.quality / 5.0)

        l, r = st.columns([1, 2])
        l.write("Mean difficulty rating: **%.2f**" % section.difficulty)
        r.progress(section.difficulty / 5.0)

        l, r = st.columns([1, 2])
        l.write("**%.0f%%** would take again" % section.professor.take_again)
        r.progress(section.professor.take_again / 100.0)

        st.write(
            "<span class='righty'>(from %d ratings)</span>"
            % len(section.ratings),
            unsafe_allow_html=True
        )
        st.divider()

        # Display the box plot
        st.plotly_chart(
            fig,
            use_container_width=True,
            # theme=None,
            config={
                'displayModeBar': False,
            }
        )

        # Display an RMP link for the professor
        st.page_link(
            "https://www.ratemyprofessors.com/search/professors/1082?q=%s"
            % section.professor.name,
            label="RateMyProfessor",
            icon=':material/open_in_new:',
        )


if not matches:
    st.write("No sections match the selected criteria.")
