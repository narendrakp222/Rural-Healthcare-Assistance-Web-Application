from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import (
    BooleanField,
    DateField,
    EmailField,
    FloatField,
    IntegerField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
    TimeField,
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional


class RegisterForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired(), Length(max=120)])
    email = EmailField("Email", validators=[DataRequired(), Email(), Length(max=160)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Create Account")


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign In")


class ProfileForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=120)])
    age = IntegerField("Age", validators=[Optional(), NumberRange(min=1, max=120)])
    gender = SelectField("Gender", choices=[("", "Select"), ("Female", "Female"), ("Male", "Male"), ("Other", "Other")])
    blood_group = SelectField(
        "Blood Group",
        choices=[("", "Select"), ("A+", "A+"), ("A-", "A-"), ("B+", "B+"), ("B-", "B-"), ("AB+", "AB+"), ("AB-", "AB-"), ("O+", "O+"), ("O-", "O-")],
    )
    height = FloatField("Height (cm)", validators=[Optional(), NumberRange(min=20, max=260)])
    weight = FloatField("Weight (kg)", validators=[Optional(), NumberRange(min=1, max=350)])
    mobile = StringField("Mobile", validators=[Optional(), Length(max=20)])
    address = TextAreaField("Address", validators=[Optional()])
    emergency_contact = StringField("Emergency Contact", validators=[Optional(), Length(max=20)])
    allergies = TextAreaField("Allergies", validators=[Optional()])
    chronic_diseases = TextAreaField("Chronic Diseases", validators=[Optional()])
    profile_picture = FileField("Profile Picture", validators=[Optional(), FileAllowed(["jpg", "jpeg", "png"], "Images only")])
    submit = SubmitField("Save Profile")


class MedicalRecordForm(FlaskForm):
    disease = StringField("Disease", validators=[DataRequired(), Length(max=120)])
    doctor = StringField("Doctor", validators=[DataRequired(), Length(max=120)])
    hospital = StringField("Hospital", validators=[DataRequired(), Length(max=160)])
    prescription = TextAreaField("Prescription", validators=[Optional()])
    diagnosis = TextAreaField("Diagnosis", validators=[Optional()])
    notes = TextAreaField("Notes", validators=[Optional()])
    date = DateField("Date", validators=[DataRequired()])
    pdf_file = FileField("Prescription PDF", validators=[Optional(), FileAllowed(["pdf"], "PDF files only")])
    submit = SubmitField("Save Record")


class MedicineForm(FlaskForm):
    medicine_name = StringField("Medicine Name", validators=[DataRequired(), Length(max=120)])
    dosage = StringField("Dosage", validators=[DataRequired(), Length(max=80)])
    morning = BooleanField("Morning")
    afternoon = BooleanField("Afternoon")
    night = BooleanField("Night")
    start_date = DateField("Start Date", validators=[DataRequired()])
    end_date = DateField("End Date", validators=[DataRequired()])
    submit = SubmitField("Save Medicine")


class AppointmentForm(FlaskForm):
    doctor = StringField("Doctor", validators=[DataRequired(), Length(max=120)])
    hospital = StringField("Hospital", validators=[DataRequired(), Length(max=160)])
    date = DateField("Date", validators=[DataRequired()])
    time = TimeField("Time", validators=[DataRequired()])
    purpose = StringField("Purpose", validators=[DataRequired(), Length(max=200)])
    status = SelectField("Status", choices=[("Scheduled", "Scheduled"), ("Completed", "Completed"), ("Cancelled", "Cancelled")])
    submit = SubmitField("Save Appointment")


class EmergencyContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=120)])
    relation = StringField("Relation", validators=[DataRequired(), Length(max=80)])
    phone = StringField("Phone Number", validators=[DataRequired(), Length(max=20)])
    submit = SubmitField("Save Contact")


class HealthArticleForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=160)])
    category = SelectField("Category", choices=[("Tips", "Tips"), ("Nutrition", "Nutrition"), ("Hygiene", "Hygiene"), ("First Aid", "First Aid")])
    summary = StringField("Summary", validators=[Optional(), Length(max=240)])
    content = TextAreaField("Content", validators=[DataRequired()])
    image = FileField("Image", validators=[Optional(), FileAllowed(["jpg", "jpeg", "png"], "Images only")])
    published = BooleanField("Published", default=True)
    submit = SubmitField("Save Article")


class HospitalForm(FlaskForm):
    name = StringField("Hospital Name", validators=[DataRequired(), Length(max=160)])
    address = TextAreaField("Address", validators=[DataRequired()])
    contact_number = StringField("Contact Number", validators=[DataRequired(), Length(max=20)])
    map_url = StringField("Google Maps URL", validators=[Optional(), Length(max=500)])
    submit = SubmitField("Save Hospital")


class FeedbackForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=120)])
    message = TextAreaField("Message", validators=[DataRequired(), Length(min=5)])
    submit = SubmitField("Send Feedback")

