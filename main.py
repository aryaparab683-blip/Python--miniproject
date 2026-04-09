from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

from models import db, User, Subject, StudySession, Task, Note, Goal, Reminder

login_manager = LoginManager()
login_manager.login_view = "auth.login"


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "replace-with-a-secure-secret"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///study_tracker.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SESSION_COOKIE_SECURE"] = False

    db.init_app(app)
    login_manager.init_app(app)

    from routes.auth import auth_bp
    from routes.main import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()
        if not User.query.first():
            create_sample_data()

    return app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_sample_data():
    sample_user = User(
        name="Study Student",
        email="student@example.com",
        password=generate_password_hash("password", method="pbkdf2:sha256", salt_length=16),
        streak=5,
    )
    db.session.add(sample_user)
    db.session.commit()

    subjects = [
        Subject(name="Math", color="#f97316", user_id=sample_user.id),
        Subject(name="Physics", color="#2563eb", user_id=sample_user.id),
        Subject(name="Language", color="#14b8a6", user_id=sample_user.id),
    ]
    db.session.add_all(subjects)
    db.session.commit()

    sessions = [
        StudySession(title="Algebra practice", duration=45, notes="Worked through equations.", subject_id=subjects[0].id, user_id=sample_user.id),
        StudySession(title="Mechanics review", duration=60, notes="Reviewed formulas for motion.", subject_id=subjects[1].id, user_id=sample_user.id),
        StudySession(title="Vocabulary flashcards", duration=30, notes="Added 20 new words.", subject_id=subjects[2].id, user_id=sample_user.id),
    ]
    goals = [
        Goal(title="Finish semester project", progress=40, target=100, user_id=sample_user.id),
        Goal(title="Complete 10 sessions this week", progress=7, target=10, user_id=sample_user.id),
    ]
    tasks = [
        Task(title="Read chapter 5", subject_id=subjects[0].id, user_id=sample_user.id),
        Task(title="Solve practice set", subject_id=subjects[1].id, user_id=sample_user.id),
    ]
    notes = [
        Note(title="Study strategy", content="Mix practice and review sessions for best retention.", user_id=sample_user.id),
    ]
    reminders = [
        Reminder(message="Start your next Pomodoro session", active=True, user_id=sample_user.id),
    ]
    db.session.add_all(sessions + goals + tasks + notes + reminders)
    db.session.commit()


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
