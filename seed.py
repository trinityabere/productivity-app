from faker import Faker

from server import create_app
from server.extensions import db
from server.models import User, Note

fake = Faker()

app = create_app()

with app.app_context():
    print("Clearing existing data...")
    Note.query.delete()
    User.query.delete()
    db.session.commit()

    print("Seeding users...")
    users = []
    demo = User(username="demo")
    demo.password_hash = "password123"
    users.append(demo)

    for _ in range(4):
        user = User(username=fake.unique.user_name())
        user.password_hash = "password123"
        users.append(user)

    db.session.add_all(users)
    db.session.commit()

    print("Seeding notes...")
    notes = []
    for user in users:
        for _ in range(5):
            notes.append(
                Note(
                    title=fake.sentence(nb_words=4),
                    content=fake.paragraph(nb_sentences=3),
                    user_id=user.id,
                )
            )

    db.session.add_all(notes)
    db.session.commit()

    print(f"Seeded {len(users)} users and {len(notes)} notes.")
    print("Demo login -> username: 'demo', password: 'password123'")