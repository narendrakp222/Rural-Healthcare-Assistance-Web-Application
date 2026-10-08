from functools import wraps

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from extensions import db
from forms import HealthArticleForm, HospitalForm
from models import Appointment, Feedback, HealthArticle, Hospital, MedicalRecord, User
from routes.user import save_upload

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)

    return wrapped


@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    stats = {
        "users": User.query.filter_by(is_admin=False).count(),
        "records": MedicalRecord.query.count(),
        "appointments": Appointment.query.count(),
        "articles": HealthArticle.query.count(),
        "hospitals": Hospital.query.count(),
        "feedback": Feedback.query.count(),
    }
    appointments = Appointment.query.order_by(Appointment.date.desc()).limit(8).all()
    feedback = Feedback.query.order_by(Feedback.created_at.desc()).limit(5).all()
    return render_template("admin_dashboard.html", stats=stats, appointments=appointments, feedback=feedback)


@admin_bp.route("/users")
@admin_required
def users():
    search = request.args.get("q", "").strip()
    query = User.query
    if search:
        like = f"%{search}%"
        query = query.filter(User.name.ilike(like) | User.email.ilike(like))
    users = query.order_by(User.created_at.desc()).all()
    return render_template("admin_users.html", users=users, search=search)


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot delete your own admin account.", "warning")
    else:
        db.session.delete(user)
        db.session.commit()
        flash("User deleted.", "info")
    return redirect(url_for("admin.users"))


@admin_bp.route("/articles", methods=["GET", "POST"])
@admin_required
def articles():
    form = HealthArticleForm()
    if form.validate_on_submit():
        article = HealthArticle()
        form.populate_obj(article)
        article.image = save_upload(form.image.data)
        db.session.add(article)
        db.session.commit()
        flash("Health article published.", "success")
        return redirect(url_for("admin.articles"))
    articles = HealthArticle.query.order_by(HealthArticle.created_at.desc()).all()
    return render_template("admin_articles.html", form=form, articles=articles)


@admin_bp.route("/articles/<int:article_id>/delete", methods=["POST"])
@admin_required
def delete_article(article_id):
    db.session.delete(HealthArticle.query.get_or_404(article_id))
    db.session.commit()
    flash("Article deleted.", "info")
    return redirect(url_for("admin.articles"))


@admin_bp.route("/hospitals", methods=["GET", "POST"])
@admin_required
def hospitals():
    form = HospitalForm()
    if form.validate_on_submit():
        hospital = Hospital()
        form.populate_obj(hospital)
        db.session.add(hospital)
        db.session.commit()
        flash("Hospital saved.", "success")
        return redirect(url_for("admin.hospitals"))
    hospitals = Hospital.query.order_by(Hospital.name.asc()).all()
    return render_template("admin_hospitals.html", form=form, hospitals=hospitals)


@admin_bp.route("/hospitals/<int:hospital_id>/delete", methods=["POST"])
@admin_required
def delete_hospital(hospital_id):
    db.session.delete(Hospital.query.get_or_404(hospital_id))
    db.session.commit()
    flash("Hospital deleted.", "info")
    return redirect(url_for("admin.hospitals"))


@admin_bp.route("/appointments")
@admin_required
def appointments():
    status = request.args.get("status", "")
    query = Appointment.query
    if status:
        query = query.filter_by(status=status)
    appointments = query.order_by(Appointment.date.desc()).all()
    return render_template("admin_appointments.html", appointments=appointments, status=status)


@admin_bp.route("/records")
@admin_required
def records():
    records = MedicalRecord.query.order_by(MedicalRecord.date.desc()).all()
    return render_template("admin_records.html", records=records)


@admin_bp.route("/feedback")
@admin_required
def feedback():
    feedback_items = Feedback.query.order_by(Feedback.created_at.desc()).all()
    return render_template("admin_feedback.html", feedback_items=feedback_items)
