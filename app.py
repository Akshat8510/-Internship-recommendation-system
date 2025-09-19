from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# Load CSV dataset (keep your internships.csv inside static/)
df = pd.read_csv("static/internships.csv")

@app.route("/")
def index():
    if "logged_in" not in session:
        return redirect(url_for("login"))
    return render_template("index.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "admin" and password == "password":
            session["logged_in"] = True
            session["username"] = username
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------------- RECOMMENDATIONS ----------------
@app.route("/recommend", methods=["POST"])
def recommend():
    if "logged_in" not in session:
        return redirect(url_for("login"))

    user_qualification = request.form.get("qualification", "")
    user_sector = request.form.get("sector", "")
    user_skills = request.form.get("skills", "")
    user_location = request.form.get("location", "")
    user_duration = request.form.get("duration", "")

    # Convert skills to list
    user_skills_list = [s.strip().lower() for s in user_skills.split(",") if s.strip()]

    recommendations = []

    for _, row in df.iterrows():
        internship_skills = [s.strip().lower() for s in row['required_skills'].split(",")]
        skill_match = len(set(user_skills_list).intersection(internship_skills))
        score = 0

        # Basic scoring
        if user_sector.lower() in row['sector'].lower():
            score += 30
        if user_qualification.lower() in row['required_education'].lower() or user_qualification.lower() == "any graduate":
            score += 20
        if skill_match > 0:
            score += int((skill_match / len(internship_skills)) * 40)
        if user_location.lower() in row['location'].lower() or row['location'].lower() == "remote":
            score += 5
        if not user_duration or user_duration.lower() in str(row.get('duration', '')).lower():
            score += 5

        if score > 0:
            recommendations.append({
                "internship_id": row['internship_id'],
                "company_name": row['company_name'],
                "title": row['title'],
                "sector": row['sector'],
                "required_skills": row['required_skills'],
                "required_education": row['required_education'],
                "location": row['location'],
                "stipend": row['stipend'],
                "match_score": score
            })

    # Sort and take top 5
    recommendations = sorted(recommendations, key=lambda x: x['match_score'], reverse=True)[:5]

    if not recommendations:
        message = "No matching internships found."
        return render_template("recommend.html", recommendations=[], message=message)

    return render_template("recommend.html", recommendations=recommendations, message="Top 5 Recommended Internships")

if __name__ == "__main__":
    app.run(debug=True)
