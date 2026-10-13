import pandas as pd


def load_student_data(file_path="data/students_master.csv"):
    """Load and validate student data."""
    df = pd.read_csv(file_path)

    required_columns = [
        "student_id",
        "student_name",
        "cgpa",
        "internal_marks",
        "attendance_pct",
        "assignment_completion_pct",
        "logins_per_week",
        "events_attended",
        "certifications",
        "aptitude_score",
        "coding_score",
        "mock_interview_score",
        "backlogs",
    ]

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    if df["student_id"].isna().any() or df["student_id"].duplicated().any():
        raise ValueError("Student IDs must be present and unique.")

    if df["student_name"].isna().any():
        raise ValueError("Student names cannot be empty.")

    percentage_columns = [
        "attendance_pct",
        "internal_marks",
        "assignment_completion_pct",
        "aptitude_score",
        "coding_score",
        "mock_interview_score",
    ]

    for col in percentage_columns:
        df[col] = pd.to_numeric(df[col], errors="raise")
        if not df[col].between(0, 100).all():
            raise ValueError(f"{col} must be between 0 and 100.")

    df["cgpa"] = pd.to_numeric(df["cgpa"], errors="raise")
    if not df["cgpa"].between(0, 10).all():
        raise ValueError("CGPA must be between 0 and 10.")

    for col in ["logins_per_week", "events_attended", "certifications", "backlogs"]:
        df[col] = pd.to_numeric(df[col], errors="raise")
        if (df[col] < 0).any():
            raise ValueError(f"{col} cannot be negative.")

    return df


def calculate_success_scores(df):
    """Calculate a transparent, rule-based demo score."""
    result = df.copy()

    result["success_score"] = (
        result["cgpa"] * 10 * 0.30
        + result["internal_marks"] * 0.20
        + result["attendance_pct"] * 0.20
        + result["assignment_completion_pct"] * 0.10
        + result["aptitude_score"] * 0.05
        + result["coding_score"] * 0.10
        + result["mock_interview_score"] * 0.05
    ).round(1)

    return result


def identify_at_risk_students(df):
    """Flag students who may benefit from additional support."""
    result = df.copy()

    result["at_risk"] = (
        (result["success_score"] < 60)
        | (result["attendance_pct"] < 60)
        | (result["backlogs"] >= 2)
    )

    return result


def recommend_interventions(row):
    """Generate supportive recommendations based on student indicators."""
    recommendations = []

    if row["attendance_pct"] < 75:
        recommendations.append(
            "Discuss attendance barriers and offer support."
        )

    if row["internal_marks"] < 60:
        recommendations.append(
            "Offer subject-specific tutoring or a study plan."
        )

    if row["assignment_completion_pct"] < 60:
        recommendations.append(
            "Help the student plan and complete pending assignments."
        )

    if row["coding_score"] < 50:
        recommendations.append(
            "Offer guided coding practice and mentoring."
        )

    if row["mock_interview_score"] < 50:
        recommendations.append(
            "Offer mock interview practice and constructive feedback."
        )

    if row["backlogs"] > 0:
        recommendations.append(
            "Create a supportive plan to address pending subjects."
        )

    if not recommendations:
        recommendations.append(
            "Continue current support and monitor progress."
        )

    return recommendations