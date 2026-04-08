from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from functools import wraps
import bcrypt
from datetime import datetime, timedelta
import os
from database import get_db_cursor, set_user_context

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if not username or not email or not password:
            flash('All fields are required', 'error')
            return render_template('register.html')

        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        try:
            with get_db_cursor(commit=True) as cursor:
                cursor.execute(
                    "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s) RETURNING id",
                    (username, email, password_hash)
                )
                user = cursor.fetchone()
                user_id = user['id']

                set_user_context(cursor, user_id)
                cursor.execute(
                    "INSERT INTO streaks (user_id, current_streak, longest_streak) VALUES (%s, 0, 0)",
                    (user_id,)
                )

            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'error')
            return render_template('register.html')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Email and password are required', 'error')
            return render_template('login.html')

        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    "SELECT id, username, email, password_hash FROM users WHERE email = %s",
                    (email,)
                )
                user = cursor.fetchone()

                if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                    session['user_id'] = str(user['id'])
                    session['username'] = user['username']
                    flash('Login successful!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid email or password', 'error')
        except Exception as e:
            flash(f'Login failed: {str(e)}', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']

    try:
        with get_db_cursor() as cursor:
            set_user_context(cursor, user_id)

            today = datetime.now().date()
            week_start = today - timedelta(days=today.weekday())

            cursor.execute("""
                SELECT COALESCE(SUM(duration), 0) as total
                FROM sessions
                WHERE user_id = %s AND DATE(start_time) = %s
            """, (user_id, today))
            daily_time = cursor.fetchone()['total']

            cursor.execute("""
                SELECT COALESCE(SUM(duration), 0) as total
                FROM sessions
                WHERE user_id = %s AND DATE(start_time) >= %s
            """, (user_id, week_start))
            weekly_time = cursor.fetchone()['total']

            cursor.execute("""
                SELECT s.name, s.color, COALESCE(SUM(sess.duration), 0) as total_time
                FROM subjects s
                LEFT JOIN sessions sess ON s.id = sess.subject_id
                WHERE s.user_id = %s
                GROUP BY s.id, s.name, s.color
                ORDER BY total_time DESC
            """, (user_id,))
            subject_stats = cursor.fetchall()

            cursor.execute("""
                SELECT sess.id, sess.duration, sess.start_time, s.name as subject_name, s.color
                FROM sessions sess
                LEFT JOIN subjects s ON sess.subject_id = s.id
                WHERE sess.user_id = %s
                ORDER BY sess.start_time DESC
                LIMIT 5
            """, (user_id,))
            recent_sessions = cursor.fetchall()

            cursor.execute("""
                SELECT current_streak, longest_streak
                FROM streaks
                WHERE user_id = %s
            """, (user_id,))
            streak_data = cursor.fetchone()

            cursor.execute("""
                SELECT COUNT(*) as total FROM tasks WHERE user_id = %s AND completed = false
            """, (user_id,))
            pending_tasks = cursor.fetchone()['total']

    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        subject_stats = []
        recent_sessions = []
        daily_time = 0
        weekly_time = 0
        streak_data = {'current_streak': 0, 'longest_streak': 0}
        pending_tasks = 0

    return render_template('dashboard.html',
                         daily_time=daily_time,
                         weekly_time=weekly_time,
                         subject_stats=subject_stats,
                         recent_sessions=recent_sessions,
                         streak_data=streak_data,
                         pending_tasks=pending_tasks)

if __name__ == '__main__':
    from routes.subjects import subjects_bp
    from routes.sessions import sessions_bp
    from routes.goals import goals_bp
    from routes.tasks import tasks_bp
    from routes.notes import notes_bp
    from routes.reminders import reminders_bp
    from routes.calendar_view import calendar_bp
    from routes.analytics import analytics_bp
    from routes.pomodoro import pomodoro_bp

    app.register_blueprint(subjects_bp)
    app.register_blueprint(sessions_bp)
    app.register_blueprint(goals_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(reminders_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(pomodoro_bp)

    app.run(debug=True, host='0.0.0.0', port=5000)
