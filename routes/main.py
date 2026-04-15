from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from models import db, Subject, StudySession, Task, Note, Goal, Reminder

main_bp = Blueprint("main", __name__, url_prefix="")


@main_bp.route("/")
@login_required
def dashboard():
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    sessions = StudySession.query.filter_by(user_id=current_user.id).order_by(StudySession.created_at.desc()).limit(5).all()
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    notes = Note.query.filter_by(user_id=current_user.id).order_by(Note.created_at.desc()).limit(4).all()
    goals = Goal.query.filter_by(user_id=current_user.id).all()
    reminders = Reminder.query.filter_by(user_id=current_user.id, active=True).all()

    total_time = sum(session.duration for session in sessions)
    subject_breakdown = [
        {
            "name": subject.name,
            "count": StudySession.query.filter_by(subject_id=subject.id, user_id=current_user.id).count(),
            "color": subject.color,
        }
        for subject in subjects
    ]
    today = datetime.utcnow().date()
    calendar_days = [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(0, 7)]

    return render_template(
        "dashboard.html",
        subjects=subjects,
        sessions=sessions,
        tasks=tasks,
        notes=notes,
        goals=goals,
        reminders=reminders,
        total_time=total_time,
        subject_breakdown=subject_breakdown,
        calendar_days=calendar_days,
    )


@main_bp.route("/sessions", methods=["GET", "POST"])
@login_required
def sessions():
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    if request.method == "POST":
        title = request.form.get("title")
        duration = request.form.get("duration", type=int)
        notes = request.form.get("notes")
        subject_id = request.form.get("subject_id", type=int)

        if not title or duration is None:
            flash("Session title and duration are required.", "error")
        else:
            session = StudySession(
                title=title,
                duration=duration,
                notes=notes,
                subject_id=subject_id or None,
                user_id=current_user.id,
            )
            db.session.add(session)
            db.session.commit()
            flash("Study session logged.", "success")
            return redirect(url_for("main.sessions"))

    sessions = StudySession.query.filter_by(user_id=current_user.id).order_by(StudySession.created_at.desc()).all()
    return render_template("sessions.html", sessions=sessions, subjects=subjects)


@main_bp.route("/sessions/edit/<int:session_id>", methods=["GET", "POST"])
@login_required
def edit_session(session_id):
    session = StudySession.query.filter_by(id=session_id, user_id=current_user.id).first_or_404()
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    if request.method == "POST":
        session.title = request.form.get("title")
        session.duration = request.form.get("duration", type=int)
        session.notes = request.form.get("notes")
        session.subject_id = request.form.get("subject_id", type=int) or None
        db.session.commit()
        flash("Study session updated.", "success")
        return redirect(url_for("main.sessions"))
    return render_template("edit_session.html", session=session, subjects=subjects)


@main_bp.route("/sessions/delete/<int:session_id>")
@login_required
def delete_session(session_id):
    session = StudySession.query.filter_by(id=session_id, user_id=current_user.id).first_or_404()
    db.session.delete(session)
    db.session.commit()
    flash("Study session deleted.", "success")
    return redirect(url_for("main.sessions"))


@main_bp.route("/subjects", methods=["GET", "POST"])
@login_required
def subjects():
    if request.method == "POST":
        name = request.form.get("name")
        color = request.form.get("color", "#6366f1")
        if not name:
            flash("Subject name is required.", "error")
        else:
            db.session.add(Subject(name=name, color=color, user_id=current_user.id))
            db.session.commit()
            flash("Subject saved.", "success")
            return redirect(url_for("main.subjects"))
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    return render_template("subjects.html", subjects=subjects)


@main_bp.route("/subjects/edit/<int:subject_id>", methods=["POST"])
@login_required
def edit_subject(subject_id):
    subject = Subject.query.filter_by(id=subject_id, user_id=current_user.id).first_or_404()
    subject.name = request.form.get("name")
    subject.color = request.form.get("color")
    db.session.commit()
    flash("Subject updated.", "success")
    return redirect(url_for("main.subjects"))


@main_bp.route("/subjects/delete/<int:subject_id>")
@login_required
def delete_subject(subject_id):
    subject = Subject.query.filter_by(id=subject_id, user_id=current_user.id).first_or_404()
    db.session.delete(subject)
    db.session.commit()
    flash("Subject deleted.", "success")
    return redirect(url_for("main.subjects"))


@main_bp.route("/tasks", methods=["GET", "POST"])
@login_required
def tasks():
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    if request.method == "POST":
        title = request.form.get("title")
        subject_id = request.form.get("subject_id", type=int)
        if not title:
            flash("Task title is required.", "error")
        else:
            db.session.add(Task(title=title, subject_id=subject_id or None, user_id=current_user.id))
            db.session.commit()
            flash("Task created.", "success")
            return redirect(url_for("main.tasks"))
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).all()
    return render_template("tasks.html", tasks=tasks, subjects=subjects)


@main_bp.route("/tasks/toggle/<int:task_id>")
@login_required
def toggle_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    task.completed = not task.completed
    db.session.commit()
    return redirect(url_for("main.tasks"))


@main_bp.route("/tasks/delete/<int:task_id>")
@login_required
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    db.session.delete(task)
    db.session.commit()
    flash("Task removed.", "success")
    return redirect(url_for("main.tasks"))


@main_bp.route("/notes", methods=["GET", "POST"])
@login_required
def notes():
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        if not title or not content:
            flash("Title and content are required.", "error")
        else:
            db.session.add(Note(title=title, content=content, user_id=current_user.id))
            db.session.commit()
            flash("Note saved.", "success")
            return redirect(url_for("main.notes"))
    notes = Note.query.filter_by(user_id=current_user.id).order_by(Note.created_at.desc()).all()
    return render_template("notes.html", notes=notes)


@main_bp.route("/notes/delete/<int:note_id>")
@login_required
def delete_note(note_id):
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first_or_404()
    db.session.delete(note)
    db.session.commit()
    flash("Note deleted.", "success")
    return redirect(url_for("main.notes"))


@main_bp.route("/goals", methods=["GET", "POST"])
@login_required
def goals():
    if request.method == "POST":
        title = request.form.get("title")
        progress = request.form.get("progress", type=int)
        target = request.form.get("target", type=int)
        if not title or target is None:
            flash("Goal title and target are required.", "error")
        else:
            db.session.add(Goal(title=title, progress=progress or 0, target=target or 100, user_id=current_user.id))
            db.session.commit()
            flash("Goal added.", "success")
            return redirect(url_for("main.goals"))
    goals = Goal.query.filter_by(user_id=current_user.id).all()
    return render_template("goals.html", goals=goals)


@main_bp.route("/goals/update/<int:goal_id>", methods=["POST"])
@login_required
def update_goal(goal_id):
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    goal.progress = request.form.get("progress", type=int) or 0
    db.session.commit()
    flash("Goal progress updated.", "success")
    return redirect(url_for("main.goals"))


@main_bp.route("/calendar")
@login_required
def calendar():
    sessions = StudySession.query.filter_by(user_id=current_user.id).order_by(StudySession.created_at.desc()).all()
    return render_template("calendar.html", sessions=sessions)


@main_bp.route("/profile")
@login_required
def profile():
    return render_template("profile.html")
