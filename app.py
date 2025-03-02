from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
import mysql.connector

import os

app = Flask(__name__, template_folder=os.path.abspath("templates"), static_folder=os.path.abspath("static"))
CORS(app, resources={r"/*": {"origins": "*"}})

# ✅ Fix: Create a proper function to return a fresh MySQL connection
def get_db_connection():
    try:
        db = mysql.connector.connect(
            host="bohznex7mygi00frt0oz-mysql.services.clever-cloud.com",
            user="uov0biyro1vaia0p",
            password="IFTcoV2uLVNQzYOaVjHL",
            database="bohznex7mygi00frt0oz",
            autocommit=True  # ✅ Auto-commit to prevent transaction issues
        )
        cursor = db.cursor()
        return db, cursor
    except mysql.connector.Error as err:
        print(f"⚠️ Error connecting to MySQL: {err}")
        return None, None

# ✅ Fix: Call get_db_connection() before executing any query

# Route: Redirect to index.html when the server starts
@app.route('/')
def home():
    return render_template("index.html")

# Route: User View (Ask a Question)
@app.route('/ask-question')
def user_page():
    return render_template("user.html")

# Route: Host View (View Questions)
@app.route('/host-view')
def host_page():
    return render_template("host.html")

# Route: Ask a Question Form Page
@app.route('/ask-question-form')
def ask_question_form():
    return render_template("ask_question_form.html")

# Route: Answer a Question Form Page
@app.route('/answer-question-form')
def answer_question_form():
    return render_template("answer_question_form.html")

# ✅ Fix: Fetch stored questions for the dropdown (before answering)
@app.route('/get-questions-for-answers', methods=['GET'])
def get_questions_for_answers():
    db, cursor = get_db_connection()
    if cursor is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor.execute("SELECT id, question FROM questions ORDER BY created_at DESC")
    questions = cursor.fetchall()

    db.close()  # ✅ Close connection after query execution

    return jsonify({"questions": [{"id": q[0], "question": q[1]} for q in questions]})

# ✅ Fix: Submit a question (Ensures MySQL connection)
@app.route('/submit-question', methods=['POST'])
def submit_question():
    db, cursor = get_db_connection()
    if cursor is None:
        return jsonify({"error": "Database connection failed"}), 500

    data = request.json
    name, age, question_text = data.get("name"), data.get("age"), data.get("question")

    if not name or not age or not question_text:
        return jsonify({"error": "All fields are required!"}), 400

    cursor.execute("INSERT INTO questions (name, age, question) VALUES (%s, %s, %s)", (name, age, question_text))
    db.close()  # ✅ Close connection after query execution

    return jsonify({"message": "Question submitted successfully!"}), 201

# ✅ Fix: Submit an answer (Ensures MySQL connection)
@app.route('/submit-answer', methods=['POST'])
def submit_answer():
    db, cursor = get_db_connection()
    if cursor is None:
        return jsonify({"error": "Database connection failed"}), 500

    data = request.json
    name, age, question_id, answer_text = data.get("name"), data.get("age"), data.get("questionId"), data.get("answer")

    if not name or not age or not question_id or not answer_text:
        return jsonify({"error": "All fields are required!"}), 400

    cursor.execute("INSERT INTO answers (question_id, answer, answerer_name, answerer_age) VALUES (%s, %s, %s, %s)",
                   (question_id, answer_text, name, age))
    db.close()  # ✅ Close connection after query execution

    return jsonify({"message": "Answer submitted successfully!"}), 201

# ✅ Fix: Get all questions (Ensures MySQL connection)
@app.route('/get-questions', methods=['GET'])
def get_questions():
    db, cursor = get_db_connection()
    if cursor is None:
        return jsonify({"questions": []})  # ✅ Prevents crashing when DB is empty

    # ✅ Fetch all questions first
    cursor.execute("""
        SELECT id, question, name, age, created_at 
        FROM questions 
        ORDER BY created_at DESC
    """)
    questions = cursor.fetchall()

    # ✅ Convert questions to dictionary format
    questions_dict = {
        q[0]: {
            "id": q[0],
            "question": q[1].strip(),
            "name": q[2],
            "age": q[3],
            "created_at": q[4].strftime('%Y-%m-%d %H:%M:%S'),
            "answers": []  # ✅ Answers will be added here
        }
        for q in questions
    }

    # ✅ Fetch all answers and group them under respective questions
    if questions:
        cursor.execute("""
            SELECT question_id, answer, answerer_name, answerer_age 
            FROM answers 
            WHERE question_id IN (%s)
        """ % ",".join(str(q[0]) for q in questions))
        answers = cursor.fetchall()

        for answer in answers:
            question_id, answer_text, answerer_name, answerer_age = answer

            if question_id in questions_dict:
                questions_dict[question_id]["answers"].append({
                    "answer": answer_text.strip(),
                    "answerer_name": answerer_name if answerer_name else "Anonymous",
                    "answerer_age": answerer_age if answerer_age else "Unknown"
                })

    db.close()

    return jsonify({"questions": list(questions_dict.values())})


# ✅ Fix: Get leaderboard data (Ensures MySQL connection)
@app.route('/get-leaderboard', methods=['GET'])
def get_leaderboard():
    db, cursor = get_db_connection()
    if cursor is None:
        return jsonify({"error": "Database connection failed"}), 500

    # Get top 3 questioners
    cursor.execute("""
        SELECT name, COUNT(*) as question_count 
        FROM questions 
        GROUP BY name 
        ORDER BY question_count DESC 
        LIMIT 3
    """)
    top_questioners = cursor.fetchall()

    # Get top 3 answerers
    cursor.execute("""
        SELECT answerer_name, COUNT(*) as answer_count 
        FROM answers 
        GROUP BY answerer_name 
        ORDER BY answer_count DESC 
        LIMIT 3
    """)
    top_answerers = cursor.fetchall()

    db.close()  # ✅ Close connection after query execution

    return jsonify({
        "questioners": [{"name": q[0], "count": q[1]} for q in top_questioners],
        "answerers": [{"name": a[0], "count": a[1]} for a in top_answerers]
    })

if __name__ == '__main__':
    PORT = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT, debug=True)
