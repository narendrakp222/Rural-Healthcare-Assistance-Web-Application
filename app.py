from datetime import date, time, timedelta
from pathlib import Path

from flask import Flask

from config import Config
from extensions import csrf, db, login_manager, migrate
from models import Appointment, HealthArticle, Hospital, Medicine, Profile, User


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    from routes.admin import admin_bp
    from routes.auth import auth_bp
    from routes.user import user_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()
        seed_demo_data()

    return app


def seed_demo_data():
    if User.query.filter_by(email="admin@healthcare.local").first():
        return

    admin = User(name="Admin", email="admin@healthcare.local", is_admin=True)
    admin.set_password("admin123")
    user = User(name="Demo Patient", email="patient@example.com")
    user.set_password("patient123")
    db.session.add_all([admin, user])
    db.session.flush()

    db.session.add(
        Profile(
            user_id=user.id,
            full_name="Demo Patient",
            age=42,
            gender="Female",
            blood_group="O+",
            height=162,
            weight=61,
            mobile="9876543210",
            address="Village Health Street, Rural Mandal",
            emergency_contact="9876500000",
            allergies="Dust",
            chronic_diseases="Hypertension",
        )
    )
    today = date.today()
    db.session.add_all(
        [
            Medicine(user_id=user.id, medicine_name="Amlodipine", dosage="5 mg", morning=True, start_date=today, end_date=today + timedelta(days=20)),
            Appointment(user_id=user.id, doctor="Dr. Rao", hospital="Primary Health Centre", date=today + timedelta(days=3), time=time(10, 30), purpose="Blood pressure review"),
            HealthArticle(title="Clean Drinking Water", category="Hygiene", summary="Simple practices to prevent water-borne diseases.", content="Boil drinking water, keep storage vessels covered, and wash hands before handling food.", published=True),
            HealthArticle(title="Balanced Rural Nutrition", category="Nutrition", summary="Affordable everyday nutrition tips.", content="Include pulses, seasonal vegetables, leafy greens, eggs or milk when available, and enough clean water.", published=True),
            Hospital(name="Primary Health Centre", address="Main Road, Rural Mandal", contact_number="108", map_url="https://www.google.com/maps/search/Primary+Health+Centre"),
            Hospital(name="District Government Hospital", address="District Headquarters", contact_number="104", map_url="https://www.google.com/maps/search/District+Government+Hospital"),
        ]
    )
    db.session.commit()


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
