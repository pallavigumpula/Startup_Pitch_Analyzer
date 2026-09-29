from auth.eligibility import check_eligibility
from analyzer.moa import analyze_moa
from analyzer.aoa import analyze_aoa
from analyzer.ir import analyze_ir
from analyzer.preprocessing import clean_text
from analyzer.section_detection import detect_sections
from analyzer.pvb import pvb_check
from analyzer.scoring import calculate_score, WEIGHTS
from analyzer.ai_insights import generate_suggestions, generate_questions
from analyzer.presentation import analyze_presentation
from analyzer.prediction import predict_success_probability
from analyzer.industry import classify_industry
from analyzer.investor_simulation import simulate_investor_panel
from analyzer.history_analytics import analyze_history
from utils.file_handler import extract_text_from_file
from utils.logger import get_logger
import time
from datetime import datetime
from flask import flash


from flask import Flask, render_template, request, redirect, session, make_response
import json
import os
import webbrowser
import time
import base64
import pdfkit

app = Flask(__name__)
app.secret_key = "secret123"
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB upload limit

logger = get_logger(__name__)

USER_FILE = "users.json"
LOGO_FILE = os.path.join(app.static_folder, "logo.png")


def build_metric_scores(ir, pvb, moa, aoa):
    """Map the IR/PVB/MOA/AOA verdicts (text/level based) to 0-100 numbers
    so the result page can plot them on a graph alongside the section scores."""
    ir_map = {
        "Investor Ready": 100,
        "Moderate - Needs improvement": 60,
        "Not ready for investors": 25,
    }
    level_map = {"Strong": 100, "Moderate": 60, "Weak": 30, "Missing": 0}

    return {
        "IR": ir_map.get(ir, 0),
        "PVB": 100 if pvb == "PVB Passed" else 0,
        "MOA": level_map.get((moa or {}).get("level"), 0),
        "AOA": level_map.get((aoa or {}).get("level"), 0),
    }


def get_logo_data_uri():
    # wkhtmltopdf renders report.html from a raw string with no base path,
    # so a relative /static/logo.png src won't resolve - embed it inline instead.
    try:
        with open(LOGO_FILE, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("ascii")
        return f"data:image/png;base64,{encoded}"
    except OSError:
        logger.exception("Could not read logo file for PDF report")
        return ""

# -----------------------
# Load Users
# -----------------------
def load_users():
    if not os.path.exists(USER_FILE):
        return {}

    with open(USER_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            logger.exception(f"{USER_FILE} is corrupted; falling back to an empty user store")
            return {}

# -----------------------
# Save Users
# -----------------------
def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

# -----------------------
# Login
# -----------------------
@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        users = load_users()

        if email in users and users[email]["password"] == password:
            session["user"] = email
            logger.info(f"Login succeeded: {email}")
            return redirect("/dashboard")
        else:
            logger.warning(f"Login failed for {email}")
            return "Invalid Credentials ❌"

    return render_template("login.html")

# -----------------------
# Register
# -----------------------
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        experience = request.form["experience"]
        security_answer = request.form["security_answer"].lower()

        users = load_users()

        if email in users:
            return "User already exists ❌"

        try:
            experience = int(experience)
            if experience < 0:
                return "Enter valid experience ❌"
        except ValueError:
            logger.warning(f"Registration failed for {email}: invalid experience value {experience!r}")
            return "Experience must be number ❌"

        users[email] = {
            "name": name,
            "password": password,
            "experience": experience,
            "security_answer": security_answer,
            "attempts": 0,
            "lock_time": 0
        }

        save_users(users)
        logger.info(f"New user registered: {email}")
        return redirect("/")

    return render_template("register.html")

# -----------------------
# Forgot Password
# -----------------------
import time

@app.route('/forgot', methods=["GET", "POST"])
def forgot():

    users = load_users()

    if request.method == "POST":
        email = request.form["email"]
        security_answer = request.form["security_answer"].lower()
        new_password = request.form["new_password"]

        if email not in users:
            return render_template("forgot.html", error="User not found ❌")

        user = users[email]

        # 🔒 LOCK CHECK (IMPORTANT)
        if user["lock_time"] > time.time():
            remaining = int(user["lock_time"] - time.time())
            return render_template("forgot.html", lock_time=remaining)

        # 🔓 LOCK EXPIRED - give the user a fresh set of attempts instead of
        # leaving the old count at >= 3 (which would re-lock on the very
        # next wrong answer).
        if user["lock_time"]:
            user["attempts"] = 0
            user["lock_time"] = 0

        # ❌ WRONG SECURITY ANSWER
        if user["security_answer"] != security_answer:
            user["attempts"] += 1

            if user["attempts"] >= 3:
                user["lock_time"] = time.time() + 180   # 3 mins lock
                save_users(users)
                return render_template("forgot.html", lock_time=180)

            save_users(users)
            return render_template(
                "forgot.html",
                error=f"Wrong answer ({user['attempts']}/3) ❌"
            )

        # ✅ SUCCESS
        user["password"] = new_password
        user["attempts"] = 0
        user["lock_time"] = 0

        save_users(users)

        return render_template(
            "forgot.html",
            success="Password updated successfully ✅"
        )

    # 🔥 GET REQUEST LOCK CHECK (VERY IMPORTANT)
    # (page open ayyaka kuda lock apply avvali)
    email = request.args.get("email")

    if email and email in users:
        user = users[email]
        if user["lock_time"] > time.time():
            remaining = int(user["lock_time"] - time.time())
            return render_template("forgot.html", lock_time=remaining)

    return render_template("forgot.html")
# -----------------------
# Dashboard
# -----------------------
@app.route('/dashboard')
def dashboard():
    if "user" not in session:
        return redirect("/")

    users = load_users()
    user = users[session["user"]]

    exp = user["experience"]
    eligibility = check_eligibility(exp)

    history = analyze_history(user.get("ideas", []))

    return render_template(
        "dashboard.html",
        name=user["name"],
        email=session["user"],
        level=eligibility["level"],
        experience=exp,
        ideas=user.get("ideas", []),
        history=history

    )


@app.route('/profile')
def profile():
    if "user" not in session:
        return redirect("/")

    users = load_users()
    user = users[session["user"]]

    eligibility = check_eligibility(user["experience"])
    history = analyze_history(user.get("ideas", []))

    return render_template(
        "profile.html",
        name=user["name"],
        email=session["user"],
        experience=user["experience"],
        level=eligibility["level"],
        ideas=user.get("ideas", []),
        history=history
    )
@app.route('/update_exp', methods=["POST"])
def update_exp():
    if "user" not in session:
        return redirect("/")

    new_exp = int(request.form["experience"])

    users = load_users()
    users[session["user"]]["experience"] = new_exp

    save_users(users)
    flash("✅ Experience updated successfully!") 

    return redirect("/dashboard")   # 🔥 redirect to profile

# -----------------------
# Analyze
# -----------------------

@app.route('/analyze', methods=["POST"])
def analyze():
    if "user" not in session:
        return redirect("/")

    users = load_users()
    user = users[session["user"]]

    exp = user["experience"]
    eligibility = check_eligibility(exp)

    pitch_file = request.files.get("pitch_file")
    text = ""

    try:
        if pitch_file and pitch_file.filename:
            text = extract_text_from_file(pitch_file)

        if not text.strip():
            text = request.form.get("pitch", "")

        if not text.strip():
            flash("⚠️ Please enter or upload your startup pitch.")
            return redirect("/dashboard")

        clean = clean_text(text)
        sections = detect_sections(clean)

        pvb = pvb_check(sections)

        # 🔥 SCORING (uses raw text so sentence boundaries survive for TF-IDF)
        scores, score = calculate_score(sections, text)

        # ✅ FIX KEY NAME (VERY IMPORTANT)
        scores["business"] = scores.get("business_model", 0)

        # 🔥 MULTIPLIER
        multiplier = eligibility.get("multiplier", 1)
        score *= multiplier
        scores = {k: round(v * multiplier, 2) for k, v in scores.items()}

        # 🔥 READINESS
        if score >= 80:
            readiness = "🚀 Investor Ready"
        elif score >= 60:
            readiness = "👍 Almost Ready"
        elif score >= 40:
            readiness = "⚠️ Needs Improvement"
        else:
            readiness = "🌱 Early Stage"

        # 🔥 STRENGTHS & WEAKNESSES
        strengths = []
        weaknesses = []

        section_weights = {**WEIGHTS, "business": WEIGHTS["business_model"]}

        for sec, val in scores.items():
            weight = section_weights.get(sec, 0)
            if weight and val >= weight * 0.6:
                strengths.append(f"{sec.capitalize()} is strong")
            else:
                weaknesses.append(f"{sec.capitalize()} needs improvement")

        suggestions = generate_suggestions(sections)
        questions = generate_questions(sections)

        # 🔥 AOA / MOA / IR ANALYSIS
        aoa = analyze_aoa(sections, text)
        moa = analyze_moa(sections, text)
        ir = analyze_ir(score)

        # 🔥 CHART-FRIENDLY NUMERIC VIEW OF IR / PVB / MOA / AOA (for graphs)
        metric_scores = build_metric_scores(ir, pvb, moa, aoa)

        # 🔥 PRESENTATION FEEDBACK + SUCCESS PREDICTION
        presentation = analyze_presentation(text, sections)
        prediction = predict_success_probability(score, sections)

        # 🔥 INDUSTRY CLASSIFICATION + INVESTOR PANEL SIMULATION
        industry = classify_industry(text)
        investor_panel = simulate_investor_panel(sections, score)

        # 🔥 SAVE SESSION (PDF kosam)
        session["last_result"] = {
            "scores": scores,
        "score": round(score, 2),
        "readiness": readiness,
        "level": eligibility["level"],
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": suggestions,
        "questions": questions,
        "aoa": aoa,
        "moa": moa,
        "ir": ir,
        "pvb": pvb,
        "metric_scores": metric_scores,
        "presentation": presentation,
        "prediction": prediction,
        "industry": industry,
        "investor_panel": investor_panel
        }
        users = load_users()
        email = session["user"]
        if "ideas" not in users[email]:
            users[email]["ideas"] = []

        users[email]["ideas"].append({
            "pitch": text,
             "score": round(score, 2),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "readiness": readiness,
            "industry": industry.get("industry") if industry else None
        })
        save_users(users)

        logger.info(f"Pitch analyzed for {session['user']}: score={round(score, 2)} readiness={readiness}")

    except ValueError as e:
        logger.warning(f"Pitch analysis input error for {session.get('user')}: {e}")
        flash(f"⚠️ {str(e)}")
        return redirect("/dashboard")
    except Exception:
        logger.exception(f"Unexpected error analyzing pitch for {session.get('user')}")
        flash("⚠️ Something went wrong while analyzing your pitch. Please try again.")
        return redirect("/dashboard")

# =========================================

    return render_template(
        "result.html",
    scores=scores,
    score=round(score, 2),
    readiness=readiness,
    level=eligibility["level"],
    strengths=strengths,
    weaknesses=weaknesses,
    suggestions=suggestions,
    questions=questions,
    aoa=aoa,
    moa=moa,
    ir=ir,
    pvb=pvb,
    metric_scores=metric_scores,
    presentation=presentation,
    prediction=prediction,
    industry=industry,
    investor_panel=investor_panel
    )

# -----------------------
# Download Report
# -----------------------
@app.route('/download_report')
def download_report():
    if "last_result" not in session:
        return "No data available to generate report ❌"

    data = session["last_result"]

    try:
        rendered = render_template(
            "report.html",
            scores=data["scores"],
            score=data["score"],
            readiness=data["readiness"],
            level=data["level"],
            strengths=data["strengths"],
            weaknesses=data["weaknesses"],
            aoa=data.get("aoa"),
            moa=data.get("moa"),
            ir=data.get("ir"),
            presentation=data.get("presentation"),
            prediction=data.get("prediction"),
            industry=data.get("industry"),
            investor_panel=data.get("investor_panel"),
            logo_data=get_logo_data_uri()
        )

        # 👉 IKKADA PETALI (IMPORTANT)
        config = pdfkit.configuration(
            wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
        )

        pdf = pdfkit.from_string(rendered, False, configuration=config)

        response = make_response(pdf)
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = "attachment; filename=report.pdf"

        return response

    except Exception as e:
        logger.exception(f"PDF report generation failed for {session.get('user')}")
        return f"PDF Error ❌: {str(e)}"
# -----------------------
# Logout
# -----------------------
@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect("/")

# -----------------------
# Run
# -----------------------
if __name__ == "__main__":
    app.run(debug=True)