from app import validate_career_profile


def test_valid_profile():

    profile = {
        "name": "Alex Morgan",
        "education": "undergraduate",
        "degree": "B.Tech CSE",
        "year": "Final Year",
        "targetRole": "Data Scientist",
        "targetIndustry": "Data and Analytics",
        "careerGoal": "Become a Data Scientist",
        "experienceLevel": "Fresher",
        "jobType": "Full-Time",
        "skillsToHighlight": "Python, SQL",
        "currentPurpose": "Job"
    }

    valid, message = validate_career_profile(profile)

    assert valid is True
    assert message == ""


def test_missing_required_field():

    profile = {
        "name": "",
        "education": "undergraduate",
        "degree": "B.Tech CSE",
        "year": "Final Year",
        "targetRole": "Data Scientist",
        "targetIndustry": "Data and Analytics",
        "careerGoal": "Become a Data Scientist",
        "experienceLevel": "Fresher",
        "jobType": "Full-Time",
        "skillsToHighlight": "Python",
        "currentPurpose": "Job"
    }

    valid, message = validate_career_profile(profile)

    assert valid is False
    assert "Full name" in message