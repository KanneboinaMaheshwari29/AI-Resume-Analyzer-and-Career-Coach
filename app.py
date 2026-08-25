# =====================================================
# AI-POWERED RESUME ANALYZER & CAREER RESUME COACH
# =====================================================

import os
import json
import fitz

from google import genai

from flask import (
    Flask,
    render_template,
    request,
    jsonify
)

from dotenv import load_dotenv
from werkzeug.utils import secure_filename


# =====================================================
# LOAD ENVIRONMENT VARIABLES
# =====================================================

load_dotenv()


# =====================================================
# ENVIRONMENT SETTINGS
# =====================================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL"
)

USE_AI = (
    os.getenv(
        "USE_AI",
        "false"
    )
    .strip()
    .lower()
    == "true"
)


try:

    AI_PROMPT_LIMIT = int(
        os.getenv(
            "AI_PROMPT_LIMIT",
            "8"
        )
    )

except ValueError:

    AI_PROMPT_LIMIT = 8


AI_PROMPT_LIMIT = max(
    0,
    min(
        AI_PROMPT_LIMIT,
        8
    )
)


# =====================================================
# GEMINI CLIENT
# =====================================================

gemini_client = None

if GEMINI_API_KEY:

    gemini_client = genai.Client(
        api_key=GEMINI_API_KEY
    )


# =====================================================
# FLASK APPLICATION
# =====================================================

app = Flask(__name__)


# =====================================================
# FILE SETTINGS
# =====================================================

MAX_FILE_SIZE = (
    5 * 1024 * 1024
)

ALLOWED_EXTENSIONS = {
    "pdf"
}

app.config[
    "MAX_CONTENT_LENGTH"
] = MAX_FILE_SIZE


# =====================================================
# STARTUP STATUS
# =====================================================

print(
    "\n========================================"
)

print(
    "AI Resume Analyzer"
)

print(
    "USE_AI:",
    USE_AI
)

print(
    "AI_PROMPT_LIMIT:",
    AI_PROMPT_LIMIT
)


if USE_AI and AI_PROMPT_LIMIT > 0:

    print(
        f"Gemini enabled for prompts 1 to {AI_PROMPT_LIMIT}."
    )

elif USE_AI and AI_PROMPT_LIMIT == 0:

    print(
        "Gemini is enabled, but AI_PROMPT_LIMIT=0 so no AI prompts will run."
    )

else:

    print(
        "Gemini AI calls are DISABLED."
    )


print(
    "========================================\n"
)


# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =====================================================
# LOAD PROMPT
# =====================================================

def load_prompt(filename):

    prompt_path = os.path.join(
        app.root_path,
        "prompts",
        filename
    )

    with open(
        prompt_path,
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


# =====================================================
# JSON HELPER
# =====================================================

def json_text(data):

    return json.dumps(
        data,
        indent=2,
        ensure_ascii=False
    )


# =====================================================
# SAFE INTEGER SCORE
# =====================================================

def safe_score(value):

    try:

        score = int(
            round(
                float(value)
            )
        )

    except (
        TypeError,
        ValueError
    ):

        score = 0


    return max(
        0,
        min(
            score,
            100
        )
    )


# =====================================================
# SCORE LEVEL
# =====================================================

def get_resume_level(score):

    if score >= 85:

        return "Strong Resume"

    if score >= 70:

        return (
            "Good Resume with "
            "Targeted Improvements"
        )

    if score >= 50:

        return (
            "Moderate Resume Requiring "
            "Meaningful Improvement"
        )

    if score >= 30:

        return (
            "Weak Resume Requiring "
            "Major Improvement"
        )

    return (
        "Very Weak or Highly "
        "Incomplete Resume"
    )


# =====================================================
# RECALCULATE WEIGHTED SCORE
# =====================================================

def enforce_score_methodology(
    final_report
):

    scores = final_report.get(
        "scores",
        {}
    )


    resume_quality = safe_score(
        scores.get(
            "resume_quality_score",
            0
        )
    )

    ats_score = safe_score(
        scores.get(
            "ats_score",
            0
        )
    )

    career_match = safe_score(
        scores.get(
            "career_match_score",
            0
        )
    )

    completeness = safe_score(
        scores.get(
            "content_completeness_score",
            0
        )
    )

    consistency = safe_score(
        scores.get(
            "error_consistency_score",
            0
        )
    )

    evidence = safe_score(
        scores.get(
            "content_evidence_score",
            0
        )
    )


    weighted_score = round(

        resume_quality * 0.25

        + ats_score * 0.20

        + career_match * 0.20

        + completeness * 0.15

        + consistency * 0.10

        + evidence * 0.10

    )


    scores[
        "resume_quality_score"
    ] = resume_quality

    scores[
        "ats_score"
    ] = ats_score

    scores[
        "career_match_score"
    ] = career_match

    scores[
        "content_completeness_score"
    ] = completeness

    scores[
        "error_consistency_score"
    ] = consistency

    scores[
        "content_evidence_score"
    ] = evidence

    scores[
        "overall_resume_score"
    ] = weighted_score

    scores[
        "overall_resume_level"
    ] = get_resume_level(
        weighted_score
    )


    final_report[
        "scores"
    ] = scores


    return final_report


# =====================================================
# FINAL REPORT INTEGRITY CHECK
# =====================================================

def validate_final_report(
    final_report
):

    if not isinstance(
        final_report,
        dict
    ):

        raise ValueError(
            "Prompt 8 did not return a valid report object."
        )

    scores = final_report.get(
        "scores"
    )

    if not isinstance(
        scores,
        dict
    ):

        raise ValueError(
            "Prompt 8 final report is missing the scores object."
        )

    required_scores = [
        "resume_quality_score",
        "ats_score",
        "career_match_score",
        "content_completeness_score",
        "error_consistency_score",
        "content_evidence_score",
        "overall_resume_score"
    ]

    for key in required_scores:

        if key not in scores:

            raise ValueError(
                f"Prompt 8 final report is missing score: {key}"
            )

        scores[key] = safe_score(
            scores.get(key)
        )

    final_report["scores"] = scores

    return final_report


# =====================================================
# PARSE GEMINI JSON
# =====================================================

def parse_gemini_json(
    response_text,
    prompt_number
):

    if not response_text:

        raise ValueError(
            f"Prompt {prompt_number} returned an empty response."
        )


    cleaned = (
        response_text.strip()
    )


    if cleaned.startswith(
        "```json"
    ):

        cleaned = cleaned[7:]


    elif cleaned.startswith(
        "```"
    ):

        cleaned = cleaned[3:]


    if cleaned.endswith(
        "```"
    ):

        cleaned = cleaned[:-3]


    cleaned = cleaned.strip()


    try:

        return json.loads(
            cleaned
        )


    except json.JSONDecodeError as error:

        print(
            f"\n========== INVALID JSON - PROMPT {prompt_number} =========="
        )

        print(
            cleaned
        )

        print(
            "==========================================================\n"
        )


        raise ValueError(
            f"Prompt {prompt_number} did not return valid JSON."
        ) from error


# =====================================================
# RUN GEMINI PROMPT
# =====================================================

def run_gemini_prompt(
    prompt_text,
    prompt_number
):

    if not USE_AI:

        raise ValueError(
            "Gemini is disabled."
        )


    if prompt_number > AI_PROMPT_LIMIT:

        raise ValueError(
            f"Prompt {prompt_number} exceeds AI_PROMPT_LIMIT."
        )


    if not GEMINI_API_KEY:

        raise ValueError(
            "Gemini API key is not configured."
        )


    if not GEMINI_MODEL:

        raise ValueError(
            "Gemini model is not configured."
        )


    if not gemini_client:

        raise ValueError(
            "Gemini client could not be initialized."
        )


    print(
        f"\n========== RUNNING PROMPT {prompt_number} =========="
    )


    response = (
        gemini_client
        .models
        .generate_content(
            model=GEMINI_MODEL,
            contents=prompt_text
        )
    )


    result = parse_gemini_json(
        response.text,
        prompt_number
    )


    print(
        f"Prompt {prompt_number} completed successfully."
    )

    print(
        "========================================\n"
    )


    return result


# =====================================================
# FORM PROFILE
# =====================================================

def get_career_profile():

    return {

        "name":
            request.form.get(
                "name",
                ""
            ).strip(),

        "education":
            request.form.get(
                "education",
                ""
            ).strip(),

        "degree":
            request.form.get(
                "degree",
                ""
            ).strip(),

        "year":
            request.form.get(
                "year",
                ""
            ).strip(),

        "targetRole":
            request.form.get(
                "targetRole",
                ""
            ).strip(),

        "targetIndustry":
            request.form.get(
                "targetIndustry",
                ""
            ).strip(),

        "careerGoal":
            request.form.get(
                "careerGoal",
                ""
            ).strip(),

        "experienceLevel":
            request.form.get(
                "experienceLevel",
                ""
            ).strip(),

        "jobType":
            request.form.get(
                "jobType",
                ""
            ).strip(),

        "skillsToHighlight":
            request.form.get(
                "skillsToHighlight",
                ""
            ).strip(),

        "currentPurpose":
            request.form.get(
                "currentPurpose",
                ""
            ).strip()

    }


# =====================================================
# PROFILE VALIDATION
# =====================================================

def validate_career_profile(
    profile
):

    required = {

        "name":
            "Full name",

        "education":
            "Current education",

        "degree":
            "Degree / course",

        "year":
            "Current year / stage",

        "targetRole":
            "Target job role",

        "targetIndustry":
            "Target industry",

        "careerGoal":
            "Career goal",

        "experienceLevel":
            "Experience level",

        "jobType":
            "Preferred job type",

        "currentPurpose":
            "Current purpose"

    }


    for key, label in (
        required.items()
    ):

        if not profile.get(
            key
        ):

            return (
                False,
                f"{label} is required."
            )


    return (
        True,
        ""
    )


# =====================================================
# PDF EXTENSION
# =====================================================

def allowed_file(filename):

    return (

        "." in filename

        and filename
        .rsplit(
            ".",
            1
        )[1]
        .lower()

        in ALLOWED_EXTENSIONS

    )


# =====================================================
# PDF TEXT EXTRACTION
# =====================================================

def extract_pdf_text(
    pdf_bytes
):

    document = None


    try:

        document = fitz.open(
            stream=pdf_bytes,
            filetype="pdf"
        )


        pages = []


        for page_number in range(
            document.page_count
        ):

            page = (
                document.load_page(
                    page_number
                )
            )


            pages.append(
                page.get_text(
                    "text"
                ).strip()
            )


        return {

            "success":
                True,

            "text":
                "\n\n".join(
                    pages
                ).strip(),

            "pageCount":
                document.page_count

        }


    except Exception as error:

        print(
            "\n========== PDF ERROR =========="
        )

        print(
            error
        )

        print(
            "===============================\n"
        )


        return {

            "success":
                False,

            "error":
                "The PDF could not be processed."

        }


    finally:

        if document is not None:

            try:

                document.close()

            except Exception:

                pass


# =====================================================
# CAREER PLACEHOLDERS
# =====================================================

def insert_career_fields(
    text,
    profile
):

    replacements = {

        "{TARGET_JOB_ROLE}":
            profile.get(
                "targetRole",
                ""
            ),

        "{TARGET_INDUSTRY}":
            profile.get(
                "targetIndustry",
                ""
            ),

        "{CAREER_GOAL}":
            profile.get(
                "careerGoal",
                ""
            ),

        "{EXPERIENCE_LEVEL}":
            profile.get(
                "experienceLevel",
                ""
            ),

        "{PREFERRED_JOB_TYPE}":
            profile.get(
                "jobType",
                ""
            ),

        "{SKILLS_TO_HIGHLIGHT}":
            profile.get(
                "skillsToHighlight",
                ""
            ),

        "{CURRENTLY_LOOKING_FOR}":
            profile.get(
                "currentPurpose",
                ""
            )

    }


    for placeholder, value in (
        replacements.items()
    ):

        text = text.replace(
            placeholder,
            value
        )


    return text


# =====================================================
# PROMPT 1
# RESUME EXTRACTION & STRUCTURING
# =====================================================

def prompt_1(
    resume_text
):

    template = load_prompt(
        "01-resume-structure.txt"
    )


    final_prompt = (
        template.replace(
            "{RESUME_TEXT}",
            resume_text
        )
    )


    return run_gemini_prompt(
        final_prompt,
        1
    )


# =====================================================
# PROMPT 2
# RESUME QUALITY
# =====================================================

def prompt_2(
    structured_resume
):

    template = load_prompt(
        "02-quality-analysis.txt"
    )


    final_prompt = (
        template.replace(
            "{STRUCTURED_RESUME}",
            json_text(
                structured_resume
            )
        )
    )


    return run_gemini_prompt(
        final_prompt,
        2
    )


# =====================================================
# PROMPT 3
# CAREER MATCH
# =====================================================

def prompt_3(
    structured_resume,
    profile
):

    template = load_prompt(
        "03-career-match.txt"
    )


    final_prompt = (
        template.replace(
            "{STRUCTURED_RESUME}",
            json_text(
                structured_resume
            )
        )
    )


    final_prompt = insert_career_fields(
        final_prompt,
        profile
    )


    return run_gemini_prompt(
        final_prompt,
        3
    )


# =====================================================
# PROMPT 4
# ATS ANALYSIS
# =====================================================

def prompt_4(
    structured_resume,
    profile
):

    template = load_prompt(
        "04-ats-analysis.txt"
    )


    final_prompt = (
        template.replace(
            "{STRUCTURED_RESUME}",
            json_text(
                structured_resume
            )
        )
    )


    final_prompt = insert_career_fields(
        final_prompt,
        profile
    )


    return run_gemini_prompt(
        final_prompt,
        4
    )


# =====================================================
# PROMPT 5
# ERROR DETECTION
# =====================================================

def prompt_5(
    structured_resume
):

    template = load_prompt(
        "05-error-detection.txt"
    )


    final_prompt = (
        template.replace(
            "{STRUCTURED_RESUME}",
            json_text(
                structured_resume
            )
        )
    )


    return run_gemini_prompt(
        final_prompt,
        5
    )


# =====================================================
# PROMPT 6
# MISSING INFORMATION
# =====================================================

def prompt_6(
    structured_resume,
    profile
):

    template = load_prompt(
        "06-missing-information.txt"
    )


    final_prompt = (
        template.replace(
            "{STRUCTURED_RESUME}",
            json_text(
                structured_resume
            )
        )
    )


    final_prompt = insert_career_fields(
        final_prompt,
        profile
    )


    return run_gemini_prompt(
        final_prompt,
        6
    )


# =====================================================
# PROMPT 7
# CONTENT IMPROVEMENT
# =====================================================

def prompt_7(
    structured_resume,
    profile,
    quality,
    errors,
    missing
):

    template = load_prompt(
        "07-content-improvement.txt"
    )


    final_prompt = (
        template

        .replace(
            "{STRUCTURED_RESUME}",
            json_text(
                structured_resume
            )
        )

        .replace(
            "{QUALITY_ANALYSIS}",
            json_text(
                quality
            )
        )

        .replace(
            "{ERROR_ANALYSIS}",
            json_text(
                errors
            )
        )

        .replace(
            "{MISSING_INFORMATION_ANALYSIS}",
            json_text(
                missing
            )
        )
    )


    final_prompt = insert_career_fields(
        final_prompt,
        profile
    )


    return run_gemini_prompt(
        final_prompt,
        7
    )


# =====================================================
# PROMPT 8
# FINAL REPORT
# =====================================================

def prompt_8(
    structured_resume,
    profile,
    quality,
    career_match,
    ats,
    errors,
    missing,
    improvement
):

    template = load_prompt(
        "08-final-report.txt"
    )


    final_prompt = (
        template

        .replace(
            "{CANDIDATE_INFORMATION}",
            json_text(
                profile
            )
        )

        .replace(
            "{STRUCTURED_RESUME}",
            json_text(
                structured_resume
            )
        )

        .replace(
            "{QUALITY_ANALYSIS}",
            json_text(
                quality
            )
        )

        .replace(
            "{CAREER_MATCH_ANALYSIS}",
            json_text(
                career_match
            )
        )

        .replace(
            "{ATS_ANALYSIS}",
            json_text(
                ats
            )
        )

        .replace(
            "{ERROR_ANALYSIS}",
            json_text(
                errors
            )
        )

        .replace(
            "{MISSING_INFORMATION_ANALYSIS}",
            json_text(
                missing
            )
        )

        .replace(
            "{CONTENT_IMPROVEMENT_ANALYSIS}",
            json_text(
                improvement
            )
        )
    )


    final_prompt = insert_career_fields(
        final_prompt,
        profile
    )


    result = run_gemini_prompt(
        final_prompt,
        8
    )


    # ---------------------------------------------
    # ENFORCE CROSS-PROMPT SCORE CONSISTENCY
    # ---------------------------------------------

    result.setdefault(
        "scores",
        {}
    )

    result["scores"]["ats_score"] = safe_score(
        ats.get(
            "ats_score",
            result["scores"].get(
                "ats_score",
                0
            )
        )
    )

    result["scores"]["career_match_score"] = safe_score(
        career_match.get(
            "career_match_score",
            result["scores"].get(
                "career_match_score",
                0
            )
        )
    )

    if ats.get(
        "ats_readiness_level"
    ):
        result["scores"]["ats_readiness_level"] = (
            ats["ats_readiness_level"]
        )

    if career_match.get(
        "career_match_level"
    ):
        result["scores"]["career_match_level"] = (
            career_match["career_match_level"]
        )


    # ---------------------------------------------
    # ENFORCE WEIGHTED SCORE FORMULA IN PYTHON
    # ---------------------------------------------

    result = enforce_score_methodology(
        result
    )

    result = validate_final_report(
        result
    )


    return result


# =====================================================
# MOCK STRUCTURED RESUME
# =====================================================

def mock_structured_resume(
    profile
):

    return {

        "candidate": {

            "name":
                profile.get(
                    "name",
                    ""
                ),

            "email":
                "",

            "phone":
                "",

            "linkedin":
                "",

            "github":
                "",

            "portfolio":
                ""

        },

        "professional_summary":
            "Mock structured resume.",

        "education":
            [],

        "technical_skills":
            [],

        "soft_skills":
            [],

        "work_experience":
            [],

        "internships":
            [],

        "projects":
            [],

        "certifications":
            [],

        "achievements":
            [],

        "extracurricular_activities":
            [],

        "interests":
            [],

        "languages":
            [],

        "other_sections":
            [],

        "detected_sections":
            [],

        "missing_common_sections":
            []

    }


# =====================================================
# MOCK QUALITY
# =====================================================

def mock_quality():

    return {

        "section_analysis":
            {},

        "resume_strengths": [
            "Mock strength."
        ],

        "critical_quality_issues": [
            "Mock quality issue."
        ],

        "unnecessary_or_low_value_content":
            [],

        "quality_priorities": {

            "high": [
                "Mock quality improvement."
            ],

            "medium":
                [],

            "low":
                []

        },

        "overall_quality_summary":
            "Mock quality analysis."

    }


# =====================================================
# MOCK CAREER MATCH
# =====================================================

def mock_career_match(
    profile
):

    return {

        "target_profile": {

            "target_job_role":
                profile.get(
                    "targetRole",
                    ""
                )

        },

        "career_match_score":
            72,

        "career_match_level":
            "Good alignment with some gaps",

        "alignment_analysis":
            {},

        "relevant_existing_skills":
            [],

        "weakly_demonstrated_skills":
            [],

        "potentially_useful_missing_skills":
            [],

        "relevant_projects":
            [],

        "strongest_alignment_points": [
            "Mock alignment point."
        ],

        "career_alignment_gaps": [
            "Mock alignment gap."
        ],

        "recommended_focus_areas":
            [],

        "career_match_summary":
            "Mock career analysis."

    }


# =====================================================
# MOCK ATS
# =====================================================

def mock_ats():

    return {

        "ats_score":
            74,

        "ats_readiness_level":
            "Good ATS readiness with some improvements",

        "score_disclaimer":
            "Mock advisory score.",

        "section_heading_analysis":
            {},

        "keyword_analysis": {

            "present_relevant_keywords":
                [],

            "weakly_represented_keywords":
                [],

            "potentially_useful_missing_keywords":
                []

        },

        "content_visibility":
            {},

        "parsing_and_readability":
            {},

        "ats_issues":
            [],

        "ats_strengths": [
            "Mock ATS strength."
        ],

        "priority_ats_improvements": {

            "high": [
                "Mock ATS improvement."
            ],

            "medium":
                [],

            "low":
                []

        },

        "ats_summary":
            "Mock ATS analysis."

    }


# =====================================================
# MOCK ERRORS
# =====================================================

def mock_errors():

    return {

        "errors_found":
            True,

        "error_count":
            1,

        "errors":
            [],

        "consistency_checks":
            {},

        "repetitive_content":
            [],

        "items_needing_candidate_verification":
            [],

        "strong_writing_examples":
            [],

        "priority_corrections": {

            "high":
                [],

            "medium": [
                "Mock wording improvement."
            ],

            "low":
                []

        },

        "error_detection_summary":
            "Mock error analysis."

    }


# =====================================================
# MOCK MISSING
# =====================================================

def mock_missing():

    return {

        "missing_information":
            [],

        "incomplete_information":
            [],

        "weakly_demonstrated_information":
            [],

        "project_completeness":
            [],

        "contact_and_links":
            {},

        "optional_improvements":
            [],

        "not_applicable_items":
            [],

        "priority_missing_information": {

            "high":
                [],

            "medium":
                [],

            "low":
                []

        },

        "completeness_summary":
            "Mock missing-information analysis."

    }


# =====================================================
# MOCK CONTENT IMPROVEMENT
# =====================================================

def mock_improvement():

    return {

        "professional_summary": {

            "original":
                "",

            "improved":
                "Mock improved professional summary.",

            "changes_made":
                [],

            "information_needed":
                []

        },

        "skills_presentation":
            {},

        "project_improvements":
            [],

        "work_experience_improvements":
            [],

        "internship_improvements":
            [],

        "education_improvements":
            [],

        "certification_improvements":
            [],

        "achievement_improvements":
            [],

        "soft_skill_recommendations":
            [],

        "repetition_reductions":
            [],

        "wording_improvements":
            [],

        "information_to_collect_before_rewriting":
            [],

        "future_development_areas":
            [],

        "priority_content_improvements": {

            "high":
                [],

            "medium":
                [],

            "low":
                []

        },

        "content_improvement_summary":
            "Mock content improvement."

    }


# =====================================================
# MOCK FINAL REPORT
# =====================================================

def mock_final_report(
    profile
):

    # -------------------------------------------------
    # MOCK COMPONENT SCORES
    # -------------------------------------------------

    resume_quality_score = 78
    ats_score = 74
    career_match_score = 72
    content_completeness_score = 80
    error_consistency_score = 85
    content_evidence_score = 60


    # -------------------------------------------------
    # APPLY REAL WEIGHTED FORMULA
    # -------------------------------------------------

    overall_score = round(

        resume_quality_score * 0.25

        + ats_score * 0.20

        + career_match_score * 0.20

        + content_completeness_score * 0.15

        + error_consistency_score * 0.10

        + content_evidence_score * 0.10

    )


    return {

        "report_title":
            "AI-Powered Resume Review",

        "candidate_name":
            profile.get(
                "name",
                ""
            ),

        "target_job_role":
            profile.get(
                "targetRole",
                ""
            ),

        "scores": {

            "resume_quality_score":
                resume_quality_score,

            "ats_score":
                ats_score,

            "career_match_score":
                career_match_score,

            "content_completeness_score":
                content_completeness_score,

            "error_consistency_score":
                error_consistency_score,

            "content_evidence_score":
                content_evidence_score,

            "overall_resume_score":
                overall_score,

            "overall_resume_level":
                get_resume_level(
                    overall_score
                ),

            "ats_readiness_level":
                "Good ATS readiness with some improvements",

            "career_match_level":
                "Good alignment with some gaps"

        },

        "score_disclaimer":
            (
                "Scores are mock development values "
                "calculated using the project scoring methodology."
            ),

        "executive_summary":
            "Development-mode final report.",


        # -------------------------------------------------
        # OLD FRONTEND-COMPATIBLE FORMAT
        # -------------------------------------------------

        "resume_strengths": [

            {

                "strength":
                    "Development-mode example strength",

                "evidence":
                    "Used only for interface testing."

            }

        ],

        "key_problems": [

            {

                "issue":
                    "Development-mode example issue",

                "why_it_matters":
                    "Used only for testing.",

                "priority":
                    "high",

                "recommended_action":
                    "Replace with real AI analysis."

            }

        ],

        "missing_or_incomplete_information":
            [],

        "errors_and_consistency": {

            "error_count":
                1,

            "important_errors": [
                "Mock wording issue."
            ],

            "items_needing_verification":
                []

        },

        "ats_review": {

            "score":
                ats_score,

            "strengths": [
                "Mock ATS strength."
            ],

            "issues": [
                "Mock ATS issue."
            ],

            "present_keywords":
                [],

            "potentially_useful_missing_keywords":
                [],

            "recommendations": [
                "Mock ATS recommendation."
            ]

        },

        "career_goal_review": {

            "score":
                career_match_score,

            "strong_alignment_points": [
                "Mock career alignment."
            ],

            "alignment_gaps": [
                "Mock career gap."
            ],

            "relevant_existing_skills":
                [],

            "future_development_areas":
                []

        },

        "content_improvements": {

            "improved_professional_summary":
                "Mock improved summary.",

            "project_improvements":
                [],

            "wording_improvements":
                []

        },

        "priority_action_plan": {

            "high": [
                "Mock high-priority action."
            ],

            "medium": [
                "Mock medium-priority action."
            ],

            "low": [
                "Mock low-priority action."
            ]

        },

        "top_5_actions": [

            {

                "rank":
                    1,

                "action":
                    "Improve the strongest project description.",

                "reason":
                    "Mock UI testing action."

            }

        ],

        "final_summary":
            "Development-mode final report."

    }


# =====================================================
# NORMALIZE NEW PROMPT 8 RESULT
# FOR EXISTING FRONTEND
# =====================================================

def normalize_final_report(
    report
):

    scores = report.get(
        "scores",
        {}
    )


    # -------------------------------------------------
    # STRENGTHS
    # -------------------------------------------------

    normalized_strengths = []


    for item in report.get(
        "resume_strengths",
        []
    ):

        if isinstance(
            item,
            dict
        ):

            normalized_strengths.append({

                "strength":
                    item.get(
                        "strength"
                    )
                    or item.get(
                        "title",
                        ""
                    ),

                "evidence":
                    item.get(
                        "evidence"
                    )
                    or item.get(
                        "details",
                        ""
                    )

            })


        elif isinstance(
            item,
            str
        ):

            normalized_strengths.append({

                "strength":
                    item,

                "evidence":
                    ""

            })


    # -------------------------------------------------
    # KEY PROBLEMS
    # -------------------------------------------------

    normalized_problems = []


    for item in report.get(
        "key_problems",
        []
    ):

        if not isinstance(
            item,
            dict
        ):

            continue


        normalized_problems.append({

            "issue":
                item.get(
                    "issue"
                )
                or item.get(
                    "title",
                    ""
                ),

            "why_it_matters":
                item.get(
                    "why_it_matters",
                    ""
                ),

            "priority":
                item.get(
                    "priority"
                )
                or item.get(
                    "severity",
                    ""
                ),

            "recommended_action":
                item.get(
                    "recommended_action"
                )
                or item.get(
                    "action",
                    ""
                )

        })


    # -------------------------------------------------
    # ATS
    # -------------------------------------------------

    new_ats = report.get(
        "ats_readiness",
        {}
    )


    ats_review = {

        "score":
            scores.get(
                "ats_score",
                0
            ),

        "strengths":
            new_ats.get(
                "strengths",
                []
            ),

        "issues":
            new_ats.get(
                "issues",
                []
            ),

        "present_keywords":
            new_ats.get(
                "present_keywords",
                []
            ),

        "potentially_useful_missing_keywords":
            [],

        "recommendations":
            new_ats.get(
                "recommendations",
                []
            )

    }


    # -------------------------------------------------
    # CAREER MATCH
    # -------------------------------------------------

    new_career = report.get(
        "career_goal_match",
        {}
    )


    career_review = {

        "score":
            scores.get(
                "career_match_score",
                0
            ),

        "strong_alignment_points":
            new_career.get(
                "strong_alignment",
                []
            ),

        "alignment_gaps":
            new_career.get(
                "alignment_gaps",
                []
            ),

        "relevant_existing_skills":
            new_career.get(
                "existing_relevant_skills",
                []
            ),

        "future_development_areas":
            new_career.get(
                "future_development",
                []
            )

    }


    # -------------------------------------------------
    # MISSING INFORMATION
    # -------------------------------------------------

    normalized_missing = []


    for item in report.get(
        "missing_information",
        []
    ):

        if not isinstance(
            item,
            dict
        ):

            continue


        normalized_missing.append({

            "item":
                item.get(
                    "category",
                    ""
                ),

            "classification":
                item.get(
                    "status",
                    ""
                ),

            "priority":
                item.get(
                    "importance",
                    ""
                ),

            "recommendation":
                item.get(
                    "recommendation",
                    ""
                )

        })


    # -------------------------------------------------
    # ERRORS
    # -------------------------------------------------

    new_errors = report.get(
        "errors_and_consistency",
        {}
    )


    errors_and_consistency = {

        "error_count":
            new_errors.get(
                "detected_issue_count",
                0
            ),

        "important_errors":
            new_errors.get(
                "issues",
                []
            ),

        "items_needing_verification":
            []

    }


    # -------------------------------------------------
    # CONTENT IMPROVEMENTS
    # -------------------------------------------------

    new_content = report.get(
        "content_improvements",
        {}
    )


    content_improvements = {

        "improved_professional_summary":
            new_content.get(
                "suggested_professional_summary",
                ""
            ),

        "project_improvements":
            new_content.get(
                "project_improvements",
                []
            ),

        "wording_improvements":
            new_content.get(
                "wording_improvements",
                []
            )

    }


    # -------------------------------------------------
    # PRIORITY PLAN
    # -------------------------------------------------

    new_priority = report.get(
        "priority_improvement_plan",
        {}
    )


    priority_action_plan = {

        "high":
            new_priority.get(
                "high_priority",
                []
            ),

        "medium":
            new_priority.get(
                "medium_priority",
                []
            ),

        "low":
            new_priority.get(
                "low_priority",
                []
            )

    }


    # -------------------------------------------------
    # TOP ACTIONS
    # -------------------------------------------------

    normalized_actions = []


    for item in report.get(
        "top_actions",
        []
    ):

        if not isinstance(
            item,
            dict
        ):

            continue


        title = item.get(
            "title",
            ""
        )

        action = item.get(
            "action",
            ""
        )


        normalized_actions.append({

            "rank":
                item.get(
                    "priority",
                    len(
                        normalized_actions
                    ) + 1
                ),

            "action":
                (
                    f"{title}: {action}"
                    if title
                    and action
                    else title
                    or action
                ),

            "reason":
                ""

        })


    # -------------------------------------------------
    # FINAL FRONTEND FORMAT
    # -------------------------------------------------

    return {

        "report_title":
            report.get(
                "report_title",
                "AI-Powered Resume Review"
            ),

        "candidate_name":
            report.get(
                "candidate_name",
                ""
            ),

        "target_job_role":
            report.get(
                "target_job_role",
                ""
            ),

        "scores":
            scores,

        "score_disclaimer":
            report.get(
                "score_disclaimer",
                ""
            ),

        "executive_summary":
            report.get(
                "executive_summary",
                ""
            ),

        "resume_strengths":
            normalized_strengths,

        "key_problems":
            normalized_problems,

        "missing_or_incomplete_information":
            normalized_missing,

        "errors_and_consistency":
            errors_and_consistency,

        "ats_review":
            ats_review,

        "career_goal_review":
            career_review,

        "content_improvements":
            content_improvements,

        "priority_action_plan":
            priority_action_plan,

        "top_5_actions":
            normalized_actions,

        "final_summary":
            report.get(
                "final_recommendation",
                ""
            )

    }


# =====================================================
# RUN CONTROLLED PIPELINE
# =====================================================

def run_pipeline(
    resume_text,
    profile
):

    # =================================================
    # FULL MOCK MODE
    # =================================================

    if not USE_AI:

        print(
            "\n========== MOCK MODE =========="
        )

        print(
            "No Gemini calls made."
        )

        print(
            "================================\n"
        )


        return {

            "structuredResume":
                mock_structured_resume(
                    profile
                ),

            "qualityAnalysis":
                mock_quality(),

            "careerMatch":
                mock_career_match(
                    profile
                ),

            "atsAnalysis":
                mock_ats(),

            "errorAnalysis":
                mock_errors(),

            "missingInformation":
                mock_missing(),

            "contentImprovement":
                mock_improvement(),

            "finalReport":
                mock_final_report(
                    profile
                )

        }


    # =================================================
    # PROMPT 1
    # =================================================

    if AI_PROMPT_LIMIT >= 1:

        structured_resume = prompt_1(
            resume_text
        )

    else:

        structured_resume = mock_structured_resume(
            profile
        )


    # =================================================
    # PROMPT 2
    # =================================================

    if AI_PROMPT_LIMIT >= 2:

        quality = prompt_2(
            structured_resume
        )

    else:

        quality = mock_quality()


    # =================================================
    # PROMPT 3
    # =================================================

    if AI_PROMPT_LIMIT >= 3:

        career_match = prompt_3(
            structured_resume,
            profile
        )

    else:

        career_match = mock_career_match(
            profile
        )


    # =================================================
    # PROMPT 4
    # =================================================

    if AI_PROMPT_LIMIT >= 4:

        ats = prompt_4(
            structured_resume,
            profile
        )

    else:

        ats = mock_ats()


    # =================================================
    # PROMPT 5
    # =================================================

    if AI_PROMPT_LIMIT >= 5:

        errors = prompt_5(
            structured_resume
        )

    else:

        errors = mock_errors()


    # =================================================
    # PROMPT 6
    # =================================================

    if AI_PROMPT_LIMIT >= 6:

        missing = prompt_6(
            structured_resume,
            profile
        )

    else:

        missing = mock_missing()


    # =================================================
    # PROMPT 7
    # =================================================

    if AI_PROMPT_LIMIT >= 7:

        improvement = prompt_7(
            structured_resume,
            profile,
            quality,
            errors,
            missing
        )

    else:

        improvement = mock_improvement()


    # =================================================
    # PROMPT 8
    # =================================================

    if AI_PROMPT_LIMIT >= 8:

        raw_final_report = prompt_8(

            structured_resume,

            profile,

            quality,

            career_match,

            ats,

            errors,

            missing,

            improvement

        )


        final_report = normalize_final_report(
            raw_final_report
        )


    else:

        final_report = mock_final_report(
            profile
        )


    return {

        "structuredResume":
            structured_resume,

        "qualityAnalysis":
            quality,

        "careerMatch":
            career_match,

        "atsAnalysis":
            ats,

        "errorAnalysis":
            errors,

        "missingInformation":
            missing,

        "contentImprovement":
            improvement,

        "finalReport":
            final_report

    }


# =====================================================
# UPLOAD + ANALYZE
# =====================================================

@app.route(
    "/api/upload-resume",
    methods=["POST"]
)
def upload_resume():

    try:

        # =================================================
        # PROFILE
        # =================================================

        profile = get_career_profile()


        valid, error_message = (
            validate_career_profile(
                profile
            )
        )


        if not valid:

            return jsonify({

                "success":
                    False,

                "error":
                    error_message

            }), 400


        # =================================================
        # FILE
        # =================================================

        if "resume" not in request.files:

            return jsonify({

                "success":
                    False,

                "error":
                    "Please select a PDF resume."

            }), 400


        file = request.files[
            "resume"
        ]


        if not file.filename:

            return jsonify({

                "success":
                    False,

                "error":
                    "No resume was selected."

            }), 400


        filename = secure_filename(
            file.filename
        )


        if not allowed_file(
            filename
        ):

            return jsonify({

                "success":
                    False,

                "error":
                    "Only PDF files are allowed."

            }), 400


        pdf_bytes = file.read()


        if not pdf_bytes:

            return jsonify({

                "success":
                    False,

                "error":
                    "The uploaded PDF is empty."

            }), 400


        if len(
            pdf_bytes
        ) > MAX_FILE_SIZE:

            return jsonify({

                "success":
                    False,

                "error":
                    "Resume file must be smaller than 5 MB."

            }), 400


        # =================================================
        # PDF EXTRACTION
        # =================================================

        extraction = extract_pdf_text(
            pdf_bytes
        )


        if not extraction[
            "success"
        ]:

            return jsonify({

                "success":
                    False,

                "error":
                    extraction[
                        "error"
                    ]

            }), 400


        resume_text = extraction[
            "text"
        ]


        page_count = extraction[
            "pageCount"
        ]


        if len(
            resume_text.strip()
        ) < 100:

            return jsonify({

                "success":
                    False,

                "error":
                    (
                        "Very little readable text was found. "
                        "Please upload a text-based resume PDF."
                    )

            }), 400


        # =================================================
        # STATUS
        # =================================================

        print(
            "\n========== ANALYSIS REQUEST =========="
        )

        print(
            "Candidate:",
            profile["name"]
        )

        print(
            "Target Role:",
            profile["targetRole"]
        )

        print(
            "USE_AI:",
            USE_AI
        )

        print(
            "AI_PROMPT_LIMIT:",
            AI_PROMPT_LIMIT
        )

        print(
            "File:",
            filename
        )

        print(
            "Pages:",
            page_count
        )

        print(
            "Characters:",
            len(
                resume_text
            )
        )

        print(
            "======================================\n"
        )


        # =================================================
        # PIPELINE
        # =================================================

        results = run_pipeline(
            resume_text,
            profile
        )


        # =================================================
        # FINAL REPORT TERMINAL CHECK
        # =================================================

        print(
            "\n========== FINAL REPORT READY =========="
        )

        print(
            "Overall Score:",
            results[
                "finalReport"
            ]
            .get(
                "scores",
                {}
            )
            .get(
                "overall_resume_score",
                0
            )
        )

        print(
            "ATS Score:",
            results[
                "finalReport"
            ]
            .get(
                "scores",
                {}
            )
            .get(
                "ats_score",
                0
            )
        )

        print(
            "Career Match:",
            results[
                "finalReport"
            ]
            .get(
                "scores",
                {}
            )
            .get(
                "career_match_score",
                0
            )
        )

        print(
            "========================================\n"
        )


        # =================================================
        # RESPONSE
        # =================================================

        return jsonify({

            "success":
                True,

            "message":
                (
                    f"AI enabled through Prompt {AI_PROMPT_LIMIT}."
                    if USE_AI
                    else
                    "Development mode. No Gemini API request was made."
                ),

            "aiEnabled":
                USE_AI,

            "promptLimit":
                AI_PROMPT_LIMIT,

            "developmentMode":
                not USE_AI,

            "partialAIMode":
                (
                    USE_AI
                    and AI_PROMPT_LIMIT < 8
                ),

            "fileName":
                filename,

            "pageCount":
                page_count,

            "characterCount":
                len(
                    resume_text
                ),

            "studentProfile":
                profile,

            "structuredResume":
                results[
                    "structuredResume"
                ],

            "qualityAnalysis":
                results[
                    "qualityAnalysis"
                ],

            "careerMatch":
                results[
                    "careerMatch"
                ],

            "atsAnalysis":
                results[
                    "atsAnalysis"
                ],

            "errorAnalysis":
                results[
                    "errorAnalysis"
                ],

            "missingInformation":
                results[
                    "missingInformation"
                ],

            "contentImprovement":
                results[
                    "contentImprovement"
                ],

            "finalReport":
                results[
                    "finalReport"
                ]

        })


    # =================================================
    # ERRORS
    # =================================================

    except Exception as error:

        print(
            "\n========== ANALYSIS ERROR =========="
        )

        print(
            type(error).__name__,
            ":",
            error
        )

        print(
            "====================================\n"
        )


        error_text = str(
            error
        )


        # ---------------------------------------------
        # QUOTA ERROR
        # ---------------------------------------------

        if (
            "429"
            in error_text

            or "RESOURCE_EXHAUSTED"
            in error_text

            or "quota"
            in error_text.lower()
        ):

            return jsonify({

                "success":
                    False,

                "error":
                    (
                        "The Gemini API usage limit "
                        "has been reached. "
                        "Please try again when the "
                        "quota becomes available."
                    )

            }), 429


        # ---------------------------------------------
        # GEMINI TEMPORARILY BUSY
        # ---------------------------------------------

        if (
            "503"
            in error_text

            or "UNAVAILABLE"
            in error_text

            or "high demand"
            in error_text.lower()
        ):

            return jsonify({

                "success":
                    False,

                "error":
                    (
                        "Gemini is temporarily busy. "
                        "Please try again later."
                    )

            }), 503


        return jsonify({

            "success":
                False,

            "error":
                error_text

        }), 500


# =====================================================
# 413 FILE TOO LARGE ERROR
# =====================================================

@app.errorhandler(413)
def file_too_large(
    error
):

    return jsonify({

        "success":
            False,

        "error":
            "Resume file must be smaller than 5 MB."

    }), 413


# =====================================================
# RUN FLASK
# =====================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )