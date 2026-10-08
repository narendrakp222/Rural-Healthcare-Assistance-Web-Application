from datetime import date, datetime, time

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db, login_manager


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    profile = db.relationship("Profile", backref="user", uselist=False, cascade="all, delete-orphan")
    records = db.relationship("MedicalRecord", backref="user", cascade="all, delete-orphan")
    medicines = db.relationship("Medicine", backref="user", cascade="all, delete-orphan")
    appointments = db.relationship("Appointment", backref="user", cascade="all, delete-orphan")
    contacts = db.relationship("EmergencyContact", backref="user", cascade="all, delete-orphan")
    feedback = db.relationship("Feedback", backref="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    full_name = db.Column(db.String(120))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(40))
    blood_group = db.Column(db.String(10))
    height = db.Column(db.Float)
    weight = db.Column(db.Float)
    mobile = db.Column(db.String(20))
    address = db.Column(db.Text)
    emergency_contact = db.Column(db.String(20))
    allergies = db.Column(db.Text)
    chronic_diseases = db.Column(db.Text)
    profile_picture = db.Column(db.String(255))

    def completion_percentage(self):
        fields = [
            self.full_name,
            self.age,
            self.gender,
            self.blood_group,
            self.height,
            self.weight,
            self.mobile,
            self.address,
            self.emergency_contact,
            self.allergies,
            self.chronic_diseases,
        ]
        return round(sum(1 for field in fields if field not in (None, "")) / len(fields) * 100)


class MedicalRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    disease = db.Column(db.String(120), nullable=False)
    doctor = db.Column(db.String(120), nullable=False)
    hospital = db.Column(db.String(160), nullable=False)
    prescription = db.Column(db.Text)
    diagnosis = db.Column(db.Text)
    notes = db.Column(db.Text)
    date = db.Column(db.Date, default=date.today)
    pdf_file = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    medicine_name = db.Column(db.String(120), nullable=False)
    dosage = db.Column(db.String(80), nullable=False)
    morning = db.Column(db.Boolean, default=False)
    afternoon = db.Column(db.Boolean, default=False)
    night = db.Column(db.Boolean, default=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    def schedule_text(self):
        parts = []
        if self.morning:
            parts.append("Morning")
        if self.afternoon:
            parts.append("Afternoon")
        if self.night:
            parts.append("Night")
        return ", ".join(parts) or "As directed"


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    doctor = db.Column(db.String(120), nullable=False)
    hospital = db.Column(db.String(160), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False, default=time(9, 0))
    purpose = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(40), default="Scheduled")


class EmergencyContact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    relation = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(20), nullable=False)


class HealthArticle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    summary = db.Column(db.String(240))
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255))
    published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    address = db.Column(db.Text, nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    map_url = db.Column(db.String(500))


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    name = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

