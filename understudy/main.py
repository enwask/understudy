import os
import pandas as pd
import plotly.express as px
import streamlit as st

from understudy.api.courses.lookup import collect_courses, collect_sections

_TAG_THRESHOLD = 10
_COURSE_THRESHOLD = 10

# Styling
_static_root: str = os.path.join(
    os.path.dirname(__file__),
    'static',
)
with open(os.path.join(_static_root, 'styles.css'), 'r') as f:
    st.markdown(
        "<style>%s</style>" % f.read(),
        unsafe_allow_html=True,
    )


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
        min_take_again=50,
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
            if num >= _TAG_THRESHOLD
        ]
        if len(wtags) > 0:
            st.write(
                ''.join(wtags),
                unsafe_allow_html=True,
            )

        # Display the box plot
        st.write("Quality/difficulty distribution (from %d ratings):"
                 % len(section.ratings))
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

# # Create a combined dataframe for values to plot
# data: list[tuple[str, float, str]] = []  # (professor, value, type of value)
# for section in sections:
#     data.extend([
#         (section.professor.name, r.quality, 'quality')
#         for r in section.ratings
#     ])
#     data.extend([
#         (section.professor.name, r.difficulty, 'difficulty')
#         for r in section.ratings
#     ])

# df = pd.DataFrame(
#     data,
#     columns=['professor', 'value', 'type'],
# )


# # Make the plot (lol)
# fig = px.box(
#     df,
#     x='value',
#     y='professor',
#     color='type',
#     title='Quality/difficulty ratings by professor',
# )
# fig.update_traces(orientation='h')
# fig.update_layout(
#     showlegend=False,
#     xaxis_title='',
#     yaxis_title='',
# )
# # fig.update_xaxes(title_text='')
# # fig.update_yaxes(visible=False)
# st.plotly_chart(
#     fig,
#     theme=None,
# )



# def _boxplot() -> alt.Chart:
#     return alt.Chart(section.frame).mark_boxplot(box={
#         'cornerRadius': 8,
#         'fillOpacity': 0.8,
#     })


# # Create charts for quality and difficulty
# charts = []
# for i, section in enumerate(sections):
#     # x will just be a position based on i
#     # y will be the quality
#     # we do this twice, once for quality and once for difficulty

#     # make the color interpolate between pastel rainbow colors
#     qual = _boxplot().encode(
#         alt.XValue(2 * i),
#         alt.Y(
#             'quality:Q',
#             title="Quality"
#         ),
#         alt.Color(
#             'x:Q',
#             scale=alt.Scale(scheme='rainbow'),
#             legend=None,
#         ),
#     )
#     diff = _boxplot().encode(
#         alt.XValue(2 * i + 1),
#         alt.Y(
#             'difficulty:Q',
#             title="Difficulty"
#         ),
#         alt.Color(
#             'x:Q',
#             scale=alt.Scale(
#                 scheme='rainbow',
#                 domain=[0, 2 * len(sections)],
#             ),
#             legend=None,
#         ),
#     )
#     charts.append(qual + diff)

#     # chart = alt.Chart(section.frame).mark_point().encode(
#     #     x='quality',
#     #     y='difficulty',
#     #     color='num_ratings',
#     #     tooltip=['professor', 'quality', 'difficulty', 'num_ratings'],
#     # ).properties(
#     #     title=section.professor.name,
#     # ).interactive()
#     # charts.append(chart)

# # Display all charts together
# st.altair_chart(
#     alt.layer(*charts),
#     use_container_width=True,
# )
