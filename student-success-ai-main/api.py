from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from analytics import (
    load_student_data,
    calculate_success_scores,
    identify_at_risk_students,
    recommend_interventions,
)

app = FastAPI(
    title="Student Success AI API",
    description="Backend API for student analytics and support recommendations",
    version="1.1.0",
)


def get_student_results():
    """Load student data and calculate analytics."""
    try:
        df = load_student_data()
        df = calculate_success_scores(df)
        df = identify_at_risk_students(df)
        return df

    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="Student dataset not found. Check data/students_master.csv.",
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to process student data: {exc}",
        )


# CHANGED: Now serves your HTML dashboard directly at the root URL
@app.get("/")
def home():
    return FileResponse("index1.html")


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }


@app.get("/students")
def get_students():
    """Return all students with success scores and risk flags."""
    df = get_student_results()
    return df.to_dict(orient="records")


@app.get("/students/{student_id}")
def get_student(student_id: str):
    """Return one student by ID."""
    df = get_student_results()

    student = df[
        df["student_id"].astype(str) == str(student_id)
    ]

    if student.empty:
        raise HTTPException(
            status_code=404,
            detail="Student not found.",
        )

    return student.iloc[0].to_dict()


@app.get("/analytics/summary")
def analytics_summary():
    """Return an overview of student results."""
    df = get_student_results()

    return {
        "total_students": int(len(df)),
        "average_success_score": round(
            float(df["success_score"].mean()), 1
        ) if len(df) else 0,
        "at_risk_students": int(df["at_risk"].sum()),
        "students_needing_support": int(
            (df["attendance_pct"] < 75).sum()
        ),
    }


@app.get("/students/{student_id}/recommendations")
def get_student_recommendations(student_id: str):
    """Return supportive recommendations for one student."""
    df = get_student_results()

    student = df[
        df["student_id"].astype(str) == str(student_id)
    ]

    if student.empty:
        raise HTTPException(
            status_code=404,
            detail="Student not found.",
        )

    row = student.iloc[0]

    return {
        "student_id": str(row["student_id"]),
        "student_name": str(row["student_name"]),
        "success_score": float(row["success_score"]),
        "at_risk": bool(row["at_risk"]),
        "recommendations": recommend_interventions(row),
    }