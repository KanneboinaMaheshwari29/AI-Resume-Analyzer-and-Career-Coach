// =====================================================
// AI RESUME ANALYZER
// =====================================================


// =====================================================
// ELEMENTS
// =====================================================

const resumeForm =
    document.getElementById("resumeForm");

const resumeInput =
    document.getElementById("resume");

const selectedFile =
    document.getElementById("selectedFile");

const selectedFileName =
    document.getElementById("selectedFileName");

const selectedFileSize =
    document.getElementById("selectedFileSize");

const resultSection =
    document.getElementById("resultSection");

const resultContent =
    document.getElementById("resultContent");

const analyzeBtn =
    document.getElementById("analyzeBtn");

const darkModeBtn =
    document.getElementById("darkModeBtn");


// =====================================================
// DARK MODE
// =====================================================

if (darkModeBtn) {

    darkModeBtn.addEventListener(
        "click",
        function () {

            document.body.classList.toggle(
                "dark-mode"
            );

            const isDark =
                document.body.classList.contains(
                    "dark-mode"
                );

            darkModeBtn.innerHTML =
                isDark
                    ? `
                        <i class="fa-solid fa-sun"></i>
                        <span>Light Mode</span>
                    `
                    : `
                        <i class="fa-solid fa-moon"></i>
                        <span>Dark Mode</span>
                    `;

        }
    );

}


// =====================================================
// FILE SIZE FORMAT
// =====================================================

function formatFileSize(bytes) {

    if (bytes < 1024) {

        return `${bytes} bytes`;

    }

    const kb =
        bytes / 1024;

    if (kb < 1024) {

        return `${kb.toFixed(1)} KB`;

    }

    const mb =
        kb / 1024;

    return `${mb.toFixed(2)} MB`;

}


// =====================================================
// FILE SELECTION
// =====================================================

if (resumeInput) {

    resumeInput.addEventListener(
        "change",
        function () {

            const file =
                resumeInput.files[0];

            if (!file) {

                selectedFile.classList.add(
                    "hidden"
                );

                return;

            }


            const isPdf =

                file.type === "application/pdf"

                || file.name
                    .toLowerCase()
                    .endsWith(".pdf");


            if (!isPdf) {

                alert(
                    "Please upload a PDF resume only."
                );

                resumeInput.value = "";

                selectedFile.classList.add(
                    "hidden"
                );

                return;

            }


            const maxSize =
                5 * 1024 * 1024;


            if (file.size > maxSize) {

                alert(
                    "Resume file must be smaller than 5 MB."
                );

                resumeInput.value = "";

                selectedFile.classList.add(
                    "hidden"
                );

                return;

            }


            selectedFileName.textContent =
                file.name;

            selectedFileSize.textContent =
                formatFileSize(
                    file.size
                );

            selectedFile.classList.remove(
                "hidden"
            );

        }
    );

}


// =====================================================
// NAME VALIDATION
// =====================================================

function validName(name) {

    const pattern =
        /^[A-Za-z][A-Za-z .'-]{1,59}$/;

    return pattern.test(
        name.trim()
    );

}


// =====================================================
// SAFE HTML
// =====================================================

function escapeHtml(text) {

    const div =
        document.createElement("div");

    div.textContent =
        text ?? "";

    return div.innerHTML;

}


// =====================================================
// CONVERT ARRAY TO LIST
// =====================================================

function arrayList(items) {

    if (
        !Array.isArray(items)
        || items.length === 0
    ) {

        return `
            <p class="empty-result">
                No major items identified.
            </p>
        `;

    }


    return `

        <ul class="report-list">

            ${items.map(
                item => `
                    <li>
                        ${escapeHtml(
                            typeof item === "string"
                                ? item
                                : JSON.stringify(item)
                        )}
                    </li>
                `
            ).join("")}

        </ul>

    `;

}


// =====================================================
// SCORE CARD
// =====================================================

function scoreCard(
    title,
    score,
    level,
    icon
) {

    return `

        <div class="score-card">

            <div class="score-icon">

                <i class="${icon}"></i>

            </div>

            <div class="score-number">

                ${Number(score) || 0}

                <span>/100</span>

            </div>

            <h3>
                ${escapeHtml(title)}
            </h3>

            <p>
                ${escapeHtml(level || "")}
            </p>

        </div>

    `;

}


// =====================================================
// PRIORITY LIST
// =====================================================

function prioritySection(
    title,
    items,
    type
) {

    if (
        !Array.isArray(items)
        || items.length === 0
    ) {

        return "";

    }


    return `

        <div class="priority-box ${type}">

            <h4>

                ${escapeHtml(title)}

            </h4>

            ${arrayList(items)}

        </div>

    `;

}


// =====================================================
// FINAL REPORT UI
// =====================================================

function createFinalReport(result) {

    const report =
        result.finalReport || {};

    const scores =
        report.scores || {};

    const strengths =
        report.resume_strengths || [];

    const problems =
        report.key_problems || [];

    const missing =
        report.missing_or_incomplete_information || [];

    const actions =
        report.top_5_actions || [];

    const priority =
        report.priority_action_plan || {};

    const ats =
        report.ats_review || {};

    const career =
        report.career_goal_review || {};

    const errors =
        report.errors_and_consistency || {};

    const content =
        report.content_improvements || {};


    const developmentNotice =
        result.developmentMode
            ? `
                <div class="development-notice">

                    <i class="fa-solid fa-flask"></i>

                    <div>

                        <strong>
                            Development Mode
                        </strong>

                        <p>
                            Mock report shown because
                            USE_AI=false. No Gemini API
                            request was made.
                        </p>

                    </div>

                </div>
            `
            : "";


    const strengthHtml =

        strengths.length

            ? strengths.map(
                item => `

                    <div class="finding-card positive">

                        <h4>
                            ${escapeHtml(
                                item.strength || ""
                            )}
                        </h4>

                        <p>
                            ${escapeHtml(
                                item.evidence || ""
                            )}
                        </p>

                    </div>

                `
            ).join("")

            : `
                <p class="empty-result">
                    No major strengths identified.
                </p>
            `;


    const problemHtml =

        problems.length

            ? problems.map(
                item => `

                    <div class="finding-card warning">

                        <div class="finding-top">

                            <h4>
                                ${escapeHtml(
                                    item.issue || ""
                                )}
                            </h4>

                            <span class="priority-tag">

                                ${escapeHtml(
                                    item.priority || ""
                                )}

                            </span>

                        </div>

                        <p>

                            <strong>
                                Why it matters:
                            </strong>

                            ${escapeHtml(
                                item.why_it_matters || ""
                            )}

                        </p>

                        <p>

                            <strong>
                                Action:
                            </strong>

                            ${escapeHtml(
                                item.recommended_action || ""
                            )}

                        </p>

                    </div>

                `
            ).join("")

            : `
                <p class="empty-result">
                    No critical problems identified.
                </p>
            `;


    const actionHtml =

        actions.length

            ? actions.map(
                item => `

                    <div class="action-item">

                        <div class="action-number">

                            ${escapeHtml(
                                String(item.rank || "")
                            )}

                        </div>

                        <div>

                            <h4>
                                ${escapeHtml(
                                    item.action || ""
                                )}
                            </h4>

                            <p>
                                ${escapeHtml(
                                    item.reason || ""
                                )}
                            </p>

                        </div>

                    </div>

                `
            ).join("")

            : `
                <p class="empty-result">
                    No priority actions available.
                </p>
            `;


    const missingHtml =

        missing.length

            ? missing.map(
                item => `

                    <div class="simple-finding">

                        <strong>
                            ${escapeHtml(
                                item.item || ""
                            )}
                        </strong>

                        <span>

                            ${escapeHtml(
                                item.classification || ""
                            )}

                            •

                            ${escapeHtml(
                                item.priority || ""
                            )}

                        </span>

                        <p>
                            ${escapeHtml(
                                item.recommendation || ""
                            )}
                        </p>

                    </div>

                `
            ).join("")

            : `
                <p class="empty-result">
                    No major missing information identified.
                </p>
            `;


    return `

        ${developmentNotice}


        <!-- =========================================
             REPORT HEADER
        ========================================== -->

        <div class="report-header">

            <div>

                <span class="report-badge">

                    <i class="fa-solid fa-wand-magic-sparkles"></i>

                    AI Resume Review

                </span>


                <h2>

                    ${escapeHtml(
                        report.report_title
                        || "AI-Powered Resume Review"
                    )}

                </h2>


                <p>

                    ${escapeHtml(
                        report.candidate_name || ""
                    )}

                    ${report.target_job_role
                        ? ` • Target Role: ${
                            escapeHtml(
                                report.target_job_role
                            )
                        }`
                        : ""
                    }

                </p>

            </div>

        </div>


        <!-- =========================================
             SCORES
        ========================================== -->

        <div class="score-grid">

            ${scoreCard(
                "Overall Resume",
                scores.overall_resume_score,
                scores.overall_resume_level,
                "fa-solid fa-file-circle-check"
            )}

            ${scoreCard(
                "ATS Readiness",
                scores.ats_score,
                scores.ats_readiness_level,
                "fa-solid fa-robot"
            )}

            ${scoreCard(
                "Career Match",
                scores.career_match_score,
                scores.career_match_level,
                "fa-solid fa-bullseye"
            )}

        </div>


        <div class="score-disclaimer">

            <i class="fa-solid fa-circle-info"></i>

            ${escapeHtml(
                report.score_disclaimer || ""
            )}

        </div>


        <!-- =========================================
             EXECUTIVE SUMMARY
        ========================================== -->

        <div class="report-block">

            <div class="report-block-heading">

                <i class="fa-solid fa-clipboard-list"></i>

                <div>

                    <h3>
                        Executive Summary
                    </h3>

                    <p>
                        Overall assessment of your current resume.
                    </p>

                </div>

            </div>


            <p class="report-text">

                ${escapeHtml(
                    report.executive_summary || ""
                )}

            </p>

        </div>


        <!-- =========================================
             STRENGTHS
        ========================================== -->

        <div class="report-block">

            <div class="report-block-heading">

                <i class="fa-solid fa-star"></i>

                <div>

                    <h3>
                        Resume Strengths
                    </h3>

                    <p>
                        What is already working well.
                    </p>

                </div>

            </div>


            <div class="findings-grid">

                ${strengthHtml}

            </div>

        </div>


        <!-- =========================================
             PROBLEMS
        ========================================== -->

        <div class="report-block">

            <div class="report-block-heading">

                <i class="fa-solid fa-triangle-exclamation"></i>

                <div>

                    <h3>
                        Key Problems
                    </h3>

                    <p>
                        The most important areas to improve.
                    </p>

                </div>

            </div>


            ${problemHtml}

        </div>


        <!-- =========================================
             ATS
        ========================================== -->

        <div class="report-block">

            <div class="report-block-heading">

                <i class="fa-solid fa-robot"></i>

                <div>

                    <h3>
                        ATS Readiness
                    </h3>

                    <p>
                        Resume structure and keyword readiness.
                    </p>

                </div>

            </div>


            <div class="two-column-report">


                <div>

                    <h4>
                        ATS Strengths
                    </h4>

                    ${arrayList(
                        ats.strengths
                    )}

                </div>


                <div>

                    <h4>
                        ATS Issues
                    </h4>

                    ${arrayList(
                        ats.issues
                    )}

                </div>


                <div>

                    <h4>
                        Present Keywords
                    </h4>

                    ${arrayList(
                        ats.present_keywords
                    )}

                </div>


                <div>

                    <h4>
                        ATS Recommendations
                    </h4>

                    ${arrayList(
                        ats.recommendations
                    )}

                </div>


            </div>

        </div>


        <!-- =========================================
             CAREER MATCH
        ========================================== -->

        <div class="report-block">

            <div class="report-block-heading">

                <i class="fa-solid fa-crosshairs"></i>

                <div>

                    <h3>
                        Career Goal Match
                    </h3>

                    <p>
                        How well your current resume supports
                        your target role.
                    </p>

                </div>

            </div>


            <div class="two-column-report">


                <div>

                    <h4>
                        Strong Alignment
                    </h4>

                    ${arrayList(
                        career.strong_alignment_points
                    )}

                </div>


                <div>

                    <h4>
                        Alignment Gaps
                    </h4>

                    ${arrayList(
                        career.alignment_gaps
                    )}

                </div>


                <div>

                    <h4>
                        Existing Relevant Skills
                    </h4>

                    ${arrayList(
                        career.relevant_existing_skills
                    )}

                </div>


                <div>

                    <h4>
                        Future Development
                    </h4>

                    ${arrayList(
                        career.future_development_areas
                    )}

                </div>


            </div>

        </div>


        <!-- =========================================
             MISSING INFORMATION
        ========================================== -->

        <div class="report-block">

            <div class="report-block-heading">

                <i class="fa-solid fa-magnifying-glass"></i>

                <div>

                    <h3>
                        Missing or Incomplete Information
                    </h3>

                    <p>
                        Information that could strengthen clarity
                        or completeness.
                    </p>

                </div>

            </div>


            ${missingHtml}

        </div>


        <!-- =========================================
             ERRORS
        ========================================== -->

        <div class="report-block">

            <div class="report-block-heading">

                <i class="fa-solid fa-spell-check"></i>

                <div>

                    <h3>
                        Errors & Consistency
                    </h3>

                    <p>
                        Important writing and consistency issues.
                    </p>

                </div>

            </div>


            <div class="error-count">

                Detected Issues:

                <strong>
                    ${Number(
                        errors.error_count
                    ) || 0}
                </strong>

            </div>


            ${arrayList(
                errors.important_errors
            )}


            ${
                Array.isArray(
                    errors.items_needing_verification
                )
                && errors.items_needing_verification.length

                    ? `
                        <h4 class="sub-heading">
                            Needs Your Verification
                        </h4>

                        ${arrayList(
                            errors.items_needing_verification
                        )}
                    `

                    : ""
            }

        </div>


        <!-- =========================================
             CONTENT IMPROVEMENTS
        ========================================== -->

        <div class="report-block">

            <div class="report-block-heading">

                <i class="fa-solid fa-pen-to-square"></i>

                <div>

                    <h3>
                        Content Improvements
                    </h3>

                    <p>
                        Suggested improvements that preserve
                        your actual experience.
                    </p>

                </div>

            </div>


            ${
                content.improved_professional_summary

                ? `
                    <div class="rewrite-box">

                        <span>
                            Suggested Professional Summary
                        </span>

                        <p>

                            ${escapeHtml(
                                content.improved_professional_summary
                            )}

                        </p>

                    </div>
                `

                : `
                    <p class="empty-result">
                        No professional-summary rewrite available.
                    </p>
                `
            }

        </div>


        <!-- =========================================
             PRIORITY PLAN
        ========================================== -->

        <div class="report-block">

            <div class="report-block-heading">

                <i class="fa-solid fa-list-check"></i>

                <div>

                    <h3>
                        Priority Improvement Plan
                    </h3>

                    <p>
                        Fix the highest-impact areas first.
                    </p>

                </div>

            </div>


            <div class="priority-grid">

                ${prioritySection(
                    "High Priority",
                    priority.high,
                    "high"
                )}

                ${prioritySection(
                    "Medium Priority",
                    priority.medium,
                    "medium"
                )}

                ${prioritySection(
                    "Low Priority",
                    priority.low,
                    "low"
                )}

            </div>

        </div>


        <!-- =========================================
             TOP ACTIONS
        ========================================== -->

        <div class="report-block">

            <div class="report-block-heading">

                <i class="fa-solid fa-rocket"></i>

                <div>

                    <h3>
                        Top Actions to Take Now
                    </h3>

                    <p>
                        Your most important resume improvements.
                    </p>

                </div>

            </div>


            <div class="action-list">

                ${actionHtml}

            </div>

        </div>


        <!-- =========================================
             FINAL SUMMARY
        ========================================== -->

        <div class="final-summary-card">

            <i class="fa-solid fa-lightbulb"></i>

            <div>

                <h3>
                    Final Recommendation
                </h3>

                <p>

                    ${escapeHtml(
                        report.final_summary || ""
                    )}

                </p>

            </div>

        </div>


        <!-- =========================================
             FILE INFORMATION
        ========================================== -->

        <div class="file-analysis-info">

            <span>
                <strong>File:</strong>
                ${escapeHtml(
                    result.fileName || ""
                )}
            </span>

            <span>
                <strong>Pages:</strong>
                ${Number(
                    result.pageCount
                ) || 0}
            </span>

            <span>
                <strong>Characters:</strong>
                ${Number(
                    result.characterCount
                ) || 0}
            </span>

        </div>


        <button
            type="button"
            class="analyze-btn new-analysis-btn"
            onclick="startNewAnalysis()"
        >

            <i class="fa-solid fa-arrow-left"></i>

            Analyze Another Resume

        </button>

    `;

}


// =====================================================
// FORM SUBMISSION
// =====================================================

if (resumeForm) {

    resumeForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            if (!resumeForm.checkValidity()) {

                resumeForm.reportValidity();

                return;

            }


            const nameInput =
                document.getElementById("name");


            if (
                !validName(
                    nameInput.value
                )
            ) {

                alert(
                    "Please enter a valid full name."
                );

                nameInput.focus();

                return;

            }


            const file =
                resumeInput.files[0];


            if (!file) {

                alert(
                    "Please select a PDF resume."
                );

                return;

            }


            const formData =
                new FormData(
                    resumeForm
                );


            analyzeBtn.disabled =
                true;


            analyzeBtn.innerHTML = `

                <i class="fa-solid fa-spinner fa-spin"></i>

                Analyzing Resume...

            `;


            resultSection.classList.remove(
                "hidden"
            );


            resultContent.innerHTML = `

                <div class="loading-report">

                    <div class="loading-icon">

                        <i class="fa-solid fa-spinner fa-spin"></i>

                    </div>

                    <h2>
                        Analyzing Your Resume
                    </h2>

                    <p>
                        Processing your PDF and preparing
                        your structured resume report.
                    </p>

                </div>

            `;


            resultSection.scrollIntoView({

                behavior: "smooth",

                block: "start"

            });


            try {


                const response =
                    await fetch(
                        "/api/upload-resume",
                        {

                            method: "POST",

                            body:
                                formData

                        }
                    );


                let result;


                try {

                    result =
                        await response.json();

                } catch {

                    throw new Error(
                        "The server returned an unexpected response."
                    );

                }


                if (
                    !response.ok
                    || !result.success
                ) {

                    throw new Error(

                        result.error
                        || "Unable to analyze the resume."

                    );

                }


                console.log(
                    "========== RESUME ANALYSIS =========="
                );

                console.log(result);

                console.log(
                    "====================================="
                );


                resultContent.innerHTML =
                    createFinalReport(
                        result
                    );


                resultSection.scrollIntoView({

                    behavior: "smooth",

                    block: "start"

                });


            } catch (error) {


                console.error(
                    "Resume Analysis Error:",
                    error
                );


                resultContent.innerHTML = `

                    <div class="loading-report">

                        <div
                            class="loading-icon error-icon"
                        >

                            <i class="fa-solid fa-triangle-exclamation"></i>

                        </div>

                        <h2>
                            Unable to Analyze Resume
                        </h2>

                        <p>
                            ${escapeHtml(
                                error.message
                            )}
                        </p>

                        <button
                            type="button"
                            class="analyze-btn"
                            onclick="startNewAnalysis()"
                            style="margin-top:20px;"
                        >

                            Try Again

                        </button>

                    </div>

                `;


            } finally {


                analyzeBtn.disabled =
                    false;


                analyzeBtn.innerHTML = `

                    <i class="fa-solid fa-wand-magic-sparkles"></i>

                    Analyze My Resume

                `;

            }

        }
    );

}


// =====================================================
// NEW ANALYSIS
// =====================================================

function startNewAnalysis() {

    resultSection.classList.add(
        "hidden"
    );


    const uploadSection =
        document.getElementById(
            "student-info"
        );


    if (uploadSection) {

        uploadSection.scrollIntoView({

            behavior: "smooth",

            block: "start"

        });

    }

}