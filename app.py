
import streamlit as st
from analytics import (
    load_student_data,
    calculate_success_scores,
    identify_at_risk_students,
    recommend_interventions,
)

st.set_page_config(
    page_title="Student Success AI",
    page_icon="🎓",
    layout="wide",
)

st.title("🎓 Student Success AI")
st.subheader("AI-Powered Student Analytics and Success Platform")
st.write(
    "Explore student performance, identify potential support needs, "
    "and generate explainable recommendations."
)

st.divider()

uploaded_file = st.file_uploader(
    "Upload student data (CSV)",
    type=["csv"],
    help="Use the required columns shown in the sample dataset.",
)

try:
    if uploaded_file is not None:
        raw_data = load_student_data(uploaded_file)
        data_source = "Uploaded CSV"
    else:
        raw_data = load_student_data()
        data_source = "Sample dataset"

    students = calculate_success_scores(raw_data)
    students = identify_at_risk_students(students)

    st.caption(f"Data source: {data_source}")

    total_students = len(students)
    at_risk_count = int(students["at_risk"].sum())
    average_score = (
        students["success_score"].mean()
        if total_students > 0
        else 0
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Students", total_students)
    col2.metric("Students At Risk", at_risk_count)
    col3.metric("Average Success Score", f"{average_score:.1f}/100")

    st.divider()
    st.header("📊 Student Performance")

    st.subheader("Success Scores by Student")

    chart_data = students[
        ["student_name", "success_score"]
    ].set_index("student_name")

    st.bar_chart(chart_data)

    st.subheader("Filter Students")

    view_option = st.radio(
        "Choose which students to display:",
        ["All Students", "At-Risk Students"],
        horizontal=True,
    )

    if view_option == "At-Risk Students":
        display_students = students[students["at_risk"]]
    else:
        display_students = students

    st.dataframe(
        display_students[
            [
                "student_id",
                "student_name",
                "attendance_pct",
                "internal_marks",
                "assignment_completion_pct",
                "success_score",
                "at_risk",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.header("🔎 Explore an Individual Student")

    selected_id = st.selectbox(
        "Select a student",
        students["student_id"].tolist(),
        format_func=lambda student_id: (
            students.loc[
                students["student_id"] == student_id,
                "student_name",
            ].iloc[0]
            + f" ({student_id})"
        ),
    )

    student = students.loc[
        students["student_id"] == selected_id
    ].iloc[0]

    st.subheader(f"Support overview: {student['student_name']}")
    st.metric("Success Score", f"{student['success_score']:.1f}/100")

    if student["at_risk"]:
        st.warning(
            "This student meets one or more demo support criteria. "
            "Review their circumstances before deciding on next steps."
        )
    else:
        st.success(
            "This student does not currently meet the demo at-risk rules. "
            "Continue monitoring their progress."
        )

    st.write("**Suggested next steps**")
    for recommendation in recommend_interventions(student):
        st.write(f"- {recommendation}")

    st.caption(
        "Demo only: scores use fixed, rule-based weights and thresholds. "
        "They are not validated predictions and should not be used alone "
        "to make decisions about students."
    )

except (ValueError, KeyError, FileNotFoundError) as error:
    st.error(f"Could not process the student data: {error}")

except Exception as error:
    st.error(
        "Something unexpected happened while loading the data. "
        "Check the CSV format and try again."
    )
    st.caption(str(error))

