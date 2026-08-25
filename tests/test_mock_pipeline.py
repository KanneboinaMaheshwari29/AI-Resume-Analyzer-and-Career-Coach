import app


def test_mock_pipeline(monkeypatch):

    monkeypatch.setattr(
        app,
        "USE_AI",
        False
    )

    profile = {

        "name":
            "Test Student",

        "education":
            "undergraduate",

        "degree":
            "B.Tech CSE",

        "year":
            "Final Year",

        "targetRole":
            "Data Scientist",

        "targetIndustry":
            "Data and Analytics",

        "careerGoal":
            "Get an entry-level Data Science role",

        "experienceLevel":
            "Fresher",

        "jobType":
            "Full-Time",

        "skillsToHighlight":
            "Python, SQL",

        "currentPurpose":
            "Job"

    }

    resume_text = """
    Test Student

    Computer Science student.

    Skills:
    Python, SQL, Machine Learning.

    Education:
    Bachelor of Technology in Computer Science.

    Projects:
    Created a machine learning project using Python.
    """

    result = app.run_pipeline(
        resume_text,
        profile
    )

    assert "structuredResume" in result
    assert "qualityAnalysis" in result
    assert "careerMatch" in result
    assert "atsAnalysis" in result
    assert "errorAnalysis" in result
    assert "missingInformation" in result
    assert "contentImprovement" in result
    assert "finalReport" in result

    assert (
        result["finalReport"]
        ["scores"]
        ["overall_resume_score"]
        == 75
    )