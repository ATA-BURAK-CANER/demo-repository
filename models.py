from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

event_categories = db.Table(
    'event_categories',
    db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id')),
)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return f'<Category {self.name}>'


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(200), nullable=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    image_url = db.Column(db.String(500), nullable=True)
    categories = db.relationship(
        'Category',
        secondary=event_categories,
        backref='events'
    )

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'start_time': self.start_time.isoformat()
            if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'image_url': self.image_url,
            'categories': [c.name for c in self.categories]
        }

    def __repr__(self):
        return f'<Event {self.title}>'


class TicketRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    event = db.relationship('Event', backref='ticket_requests')
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(50), nullable=True)
    ticket_count = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(
        db.String(50),
        nullable=False,
        default='pending'
    )

    def __repr__(self):
        return f'<TicketRequest {self.first_name} {self.last_name} - {self.event.title}>'
