from app import mock_final_report


def test_final_report_structure():

    profile = {

        "name":
            "Alex Morgan",

        "targetRole":
            "Data Scientist"

    }

    report = mock_final_report(
        profile
    )

    assert (
        report["report_title"]
        == "AI-Powered Resume Review"
    )

    assert (
        report["candidate_name"]
        == "Alex Morgan"
    )

    assert (
        report["target_job_role"]
        == "Data Scientist"
    )

    assert "scores" in report

    scores = report["scores"]

    required_scores = [

        "resume_quality_score",
        "ats_score",
        "career_match_score",
        "content_completeness_score",
        "error_consistency_score",
        "content_evidence_score",
        "overall_resume_score"

    ]

    for score_name in required_scores:

        assert score_name in scores

        assert (
            0
            <= scores[score_name]
            <= 100
        )


    assert "resume_strengths" in report
    assert "key_problems" in report
    assert "ats_review" in report
    assert "career_goal_review" in report
    assert "priority_action_plan" in report
    assert "final_summary" in report