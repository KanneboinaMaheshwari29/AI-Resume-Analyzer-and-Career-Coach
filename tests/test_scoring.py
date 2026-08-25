from app import (
    enforce_score_methodology,
    get_resume_level
)


def test_weighted_resume_score():

    report = {

        "scores": {

            "resume_quality_score": 78,
            "ats_score": 74,
            "career_match_score": 72,
            "content_completeness_score": 80,
            "error_consistency_score": 85,
            "content_evidence_score": 60

        }

    }

    result = enforce_score_methodology(
        report
    )

    scores = result["scores"]

    assert scores["overall_resume_score"] == 75

    assert (
        scores["overall_resume_level"]
        == "Good Resume with Targeted Improvements"
    )


def test_score_levels():

    assert (
        get_resume_level(90)
        == "Strong Resume"
    )

    assert (
        get_resume_level(75)
        == "Good Resume with Targeted Improvements"
    )

    assert (
        get_resume_level(60)
        == "Moderate Resume Requiring Meaningful Improvement"
    )

    assert (
        get_resume_level(40)
        == "Weak Resume Requiring Major Improvement"
    )

    assert (
        get_resume_level(20)
        == "Very Weak or Highly Incomplete Resume"
    )