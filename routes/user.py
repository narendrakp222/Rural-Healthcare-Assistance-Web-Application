from datetime import date
from pathlib import Path
from uuid import uuid4

from flask import Blueprint, current_app, flash, make_response, redirect, render_template, request, send_from_directory, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from extensions import db
from forms import AppointmentForm, EmergencyContactForm, FeedbackForm, MedicalRecordForm, MedicineForm, ProfileForm
from models import Appointment, EmergencyContact, Feedback, HealthArticle, Hospital, MedicalRecord, Medicine, Profile

user_bp = Blueprint("user", __name__, url_prefix="/user")


def save_upload(file_storage):
    if not file_storage or not file_storage.filename:
        return None
    filename = secure_filename(file_storage.filename)
    unique_name = f"{uuid4().hex}_{filename}"
    upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_storage.save(upload_dir / unique_name)
    return unique_name


def own_or_404(model, item_id):
    return model.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()


@user_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for("admin.dashboard"))
    profile = current_user.profile or Profile(user_id=current_user.id, full_name=current_user.name)
    if not profile.id:
        db.session.add(profile)
        db.session.commit()
    upcoming_medicines = Medicine.query.filter(Medicine.user_id == current_user.id, Medicine.end_date >= date.today()).order_by(Medicine.end_date.asc()).limit(5).all()
    appointments = Appointment.query.filter(Appointment.user_id == current_user.id, Appointment.date >= date.today()).order_by(Appointment.date.asc()).limit(5).all()
    records = MedicalRecord.query.filter_by(user_id=current_user.id).order_by(MedicalRecord.date.desc()).limit(5).all()
    contacts = EmergencyContact.query.filter_by(user_id=current_user.id).limit(3).all()
    articles = HealthArticle.query.filter_by(published=True).order_by(HealthArticle.created_at.desc()).limit(3).all()
    return render_template("dashboard.html", profile=profile, upcoming_medicines=upcoming_medicines, appointments=appointments, records=records, contacts=contacts, articles=articles)


@user_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    profile = current_user.profile or Profile(user_id=current_user.id, full_name=current_user.name)
    form = ProfileForm(obj=profile)
    if form.validate_on_submit():
        old_picture = profile.profile_picture
        form.populate_obj(profile)
        uploaded = save_upload(form.profile_picture.data)
        profile.profile_picture = uploaded or old_picture
        db.session.add(profile)
        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("user.profile"))
    return render_template("profile.html", form=form, profile=profile)


@user_bp.route("/medical-records", methods=["GET", "POST"])
@login_required
def medical_records():
    form = MedicalRecordForm()
    if form.validate_on_submit():
        record = MedicalRecord(user_id=current_user.id)
        form.populate_obj(record)
        record.pdf_file = save_upload(form.pdf_file.data)
        db.session.add(record)
        db.session.commit()
        flash("Medical record saved.", "success")
        return redirect(url_for("user.medical_records"))
    query = request.args.get("q", "").strip()
    records_query = MedicalRecord.query.filter_by(user_id=current_user.id)
    if query:
        like = f"%{query}%"
        records_query = records_query.filter(MedicalRecord.disease.ilike(like) | MedicalRecord.doctor.ilike(like) | MedicalRecord.hospital.ilike(like))
    records = records_query.order_by(MedicalRecord.date.desc()).all()
    return render_template("medical_records.html", form=form, records=records, query=query)


@user_bp.route("/medical-records/<int:record_id>/edit", methods=["GET", "POST"])
@login_required
def edit_record(record_id):
    record = own_or_404(MedicalRecord, record_id)
    form = MedicalRecordForm(obj=record)
    if form.validate_on_submit():
        old_pdf = record.pdf_file
        form.populate_obj(record)
        uploaded = save_upload(form.pdf_file.data)
        record.pdf_file = uploaded or old_pdf
        db.session.commit()
        flash("Medical record updated.", "success")
        return redirect(url_for("user.medical_records"))
    records = MedicalRecord.query.filter_by(user_id=current_user.id).order_by(MedicalRecord.date.desc()).all()
    return render_template("medical_records.html", form=form, records=records, query="", editing=record)


@user_bp.route("/medical-records/<int:record_id>/print")
@login_required
def print_record(record_id):
    record = own_or_404(MedicalRecord, record_id)
    return render_template("print_record.html", record=record)


@user_bp.route("/medical-records/export")
@login_required
def export_records_pdf():
    records = MedicalRecord.query.filter_by(user_id=current_user.id).order_by(MedicalRecord.date.desc()).all()
    html = render_template("records_export.html", records=records)
    response = make_response(html)
    response.headers["Content-Type"] = "text/html"
    response.headers["Content-Disposition"] = "attachment; filename=medical_records_export.html"
    return response


@user_bp.route("/medical-records/<int:record_id>/delete", methods=["POST"])
@login_required
def delete_record(record_id):
    db.session.delete(own_or_404(MedicalRecord, record_id))
    db.session.commit()
    flash("Medical record deleted.", "info")
    return redirect(url_for("user.medical_records"))


@user_bp.route("/uploads/<path:filename>")
@login_required
def uploaded_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename, as_attachment=True)


@user_bp.route("/medicine-reminders", methods=["GET", "POST"])
@login_required
def medicine_reminders():
    form = MedicineForm()
    if form.validate_on_submit():
        medicine = Medicine(user_id=current_user.id)
        form.populate_obj(medicine)
        db.session.add(medicine)
        db.session.commit()
        flash("Medicine reminder saved.", "success")
        return redirect(url_for("user.medicine_reminders"))
    medicines = Medicine.query.filter_by(user_id=current_user.id).order_by(Medicine.end_date.desc()).all()
    return render_template("medicine_reminders.html", form=form, medicines=medicines)


@user_bp.route("/medicine-reminders/<int:medicine_id>/edit", methods=["GET", "POST"])
@login_required
def edit_medicine(medicine_id):
    medicine = own_or_404(Medicine, medicine_id)
    form = MedicineForm(obj=medicine)
    if form.validate_on_submit():
        form.populate_obj(medicine)
        db.session.commit()
        flash("Medicine reminder updated.", "success")
        return redirect(url_for("user.medicine_reminders"))
    medicines = Medicine.query.filter_by(user_id=current_user.id).order_by(Medicine.end_date.desc()).all()
    return render_template("medicine_reminders.html", form=form, medicines=medicines, editing=medicine)


@user_bp.route("/medicine-reminders/<int:medicine_id>/delete", methods=["POST"])
@login_required
def delete_medicine(medicine_id):
    db.session.delete(own_or_404(Medicine, medicine_id))
    db.session.commit()
    flash("Medicine reminder deleted.", "info")
    return redirect(url_for("user.medicine_reminders"))


@user_bp.route("/appointments", methods=["GET", "POST"])
@login_required
def appointments():
    form = AppointmentForm()
    if form.validate_on_submit():
        appointment = Appointment(user_id=current_user.id)
        form.populate_obj(appointment)
        db.session.add(appointment)
        db.session.commit()
        flash("Appointment saved.", "success")
        return redirect(url_for("user.appointments"))
    appointments = Appointment.query.filter_by(user_id=current_user.id).order_by(Appointment.date.desc()).all()
    return render_template("appointments.html", form=form, appointments=appointments)


@user_bp.route("/appointments/<int:appointment_id>/edit", methods=["GET", "POST"])
@login_required
def edit_appointment(appointment_id):
    appointment = own_or_404(Appointment, appointment_id)
    form = AppointmentForm(obj=appointment)
    if form.validate_on_submit():
        form.populate_obj(appointment)
        db.session.commit()
        flash("Appointment updated.", "success")
        return redirect(url_for("user.appointments"))
    appointments = Appointment.query.filter_by(user_id=current_user.id).order_by(Appointment.date.desc()).all()
    return render_template("appointments.html", form=form, appointments=appointments, editing=appointment)


@user_bp.route("/appointments/<int:appointment_id>/delete", methods=["POST"])
@login_required
def delete_appointment(appointment_id):
    db.session.delete(own_or_404(Appointment, appointment_id))
    db.session.commit()
    flash("Appointment deleted.", "info")
    return redirect(url_for("user.appointments"))


@user_bp.route("/emergency-contacts", methods=["GET", "POST"])
@login_required
def emergency_contacts():
    form = EmergencyContactForm()
    if form.validate_on_submit():
        contact = EmergencyContact(user_id=current_user.id)
        form.populate_obj(contact)
        db.session.add(contact)
        db.session.commit()
        flash("Emergency contact saved.", "success")
        return redirect(url_for("user.emergency_contacts"))
    contacts = EmergencyContact.query.filter_by(user_id=current_user.id).all()
    return render_template("emergency_contacts.html", form=form, contacts=contacts)


@user_bp.route("/emergency-contacts/<int:contact_id>/edit", methods=["GET", "POST"])
@login_required
def edit_contact(contact_id):
    contact = own_or_404(EmergencyContact, contact_id)
    form = EmergencyContactForm(obj=contact)
    if form.validate_on_submit():
        form.populate_obj(contact)
        db.session.commit()
        flash("Emergency contact updated.", "success")
        return redirect(url_for("user.emergency_contacts"))
    contacts = EmergencyContact.query.filter_by(user_id=current_user.id).all()
    return render_template("emergency_contacts.html", form=form, contacts=contacts, editing=contact)


@user_bp.route("/emergency-contacts/<int:contact_id>/delete", methods=["POST"])
@login_required
def delete_contact(contact_id):
    db.session.delete(own_or_404(EmergencyContact, contact_id))
    db.session.commit()
    flash("Emergency contact deleted.", "info")
    return redirect(url_for("user.emergency_contacts"))


@user_bp.route("/health-articles")
@login_required
def health_articles():
    category = request.args.get("category", "")
    query = HealthArticle.query.filter_by(published=True)
    if category:
        query = query.filter_by(category=category)
    articles = query.order_by(HealthArticle.created_at.desc()).all()
    return render_template("health_articles.html", articles=articles, category=category)


@user_bp.route("/nearby-hospitals")
@login_required
def nearby_hospitals():
    hospitals = Hospital.query.order_by(Hospital.name.asc()).all()
    return render_template("nearby_hospitals.html", hospitals=hospitals)


@user_bp.route("/feedback", methods=["POST"])
@login_required
def feedback():
    form = FeedbackForm()
    if form.validate_on_submit():
        db.session.add(Feedback(user_id=current_user.id, name=form.name.data, message=form.message.data))
        db.session.commit()
        flash("Thank you for your feedback.", "success")
    else:
        flash("Please enter valid feedback.", "danger")
    return redirect(url_for("auth.index"))
