from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from models import db, Event, Category, TicketRequest
from datetime import datetime

admin_bp = Blueprint('admin', __name__, template_folder='templates')


def is_logged_in():
    return session.get('admin')


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        pwd = request.form.get('password')
        if username == 'admin' and pwd == 'test123':
            session['admin'] = True
            return redirect(url_for('admin.events'))
        flash('Kullanıcı adı veya şifre hatalı', 'danger')
    return render_template('admin/login.html')


@admin_bp.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('main.index'))


@admin_bp.route('/events')
def events():
    if not is_logged_in():
        return redirect(url_for('admin.login'))
    events = Event.query.order_by(Event.start_time).all()
    return render_template('admin/events.html', events=events)


@admin_bp.route('/events/create', methods=['GET', 'POST'])
def create_event():
    if not is_logged_in():
        return redirect(url_for('admin.login'))
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        location = request.form.get('location')
        image_url = request.form.get('image_url')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        cats = request.form.get('categories', '')
        ev = Event(
            title=title,
            description=description,
            location=location,
            image_url=image_url,
            start_time=datetime.fromisoformat(start_time)
            if start_time else datetime.utcnow(),
            end_time=datetime.fromisoformat(end_time) if end_time else None
        )
        # categories comma separated
        for name in [c.strip() for c in cats.split(',') if c.strip()]:
            cat = Category.query.filter_by(name=name).first()
            if not cat:
                cat = Category(name=name)
                db.session.add(cat)
            ev.categories.append(cat)
        db.session.add(ev)
        db.session.commit()
        flash('Event created', 'success')
        return redirect(url_for('admin.events'))
    categories = Category.query.order_by(Category.name).all()
    return render_template('admin/create_event.html', categories=categories)


@admin_bp.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
def edit_event(event_id):
    if not is_logged_in():
        return redirect(url_for('admin.login'))
    ev = Event.query.get_or_404(event_id)
    if request.method == 'POST':
        ev.title = request.form.get('title')
        ev.description = request.form.get('description')
        ev.location = request.form.get('location')
        ev.image_url = request.form.get('image_url')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        ev.start_time = (
            datetime.fromisoformat(start_time)
            if start_time else ev.start_time
        )
        ev.end_time = (
            datetime.fromisoformat(end_time)
            if end_time else ev.end_time
        )
        cats = request.form.get('categories', '')
        ev.categories.clear()
        for name in [c.strip() for c in cats.split(',') if c.strip()]:
            cat = Category.query.filter_by(name=name).first()
            if not cat:
                cat = Category(name=name)
                db.session.add(cat)
            ev.categories.append(cat)
        db.session.commit()
        flash('Event updated', 'success')
        return redirect(url_for('admin.events'))
    cats = ', '.join([c.name for c in ev.categories])
    return render_template('admin/edit_event.html', event=ev, categories=cats)


@admin_bp.route('/events/<int:event_id>/delete', methods=['POST'])
def delete_event(event_id):
    if not is_logged_in():
        return redirect(url_for('admin.login'))
    ev = Event.query.get_or_404(event_id)
    db.session.delete(ev)
    db.session.commit()
    flash('Event deleted', 'success')
    return redirect(url_for('admin.events'))


@admin_bp.route('/tickets')
def tickets():
    if not is_logged_in():
        return redirect(url_for('admin.login'))
    tickets = TicketRequest.query.order_by(
        TicketRequest.created_at.desc()
    ).all()
    return render_template('admin/tickets.html', tickets=tickets)


@admin_bp.route('/tickets/<int:ticket_id>/delete', methods=['POST'])
def delete_ticket(ticket_id):
    if not is_logged_in():
        return redirect(url_for('admin.login'))
    ticket = TicketRequest.query.get_or_404(ticket_id)
    db.session.delete(ticket)
    db.session.commit()
    flash('Bilet talebi silindi', 'success')
    return redirect(url_for('admin.tickets'))


@admin_bp.route('/tickets/<int:ticket_id>/status', methods=['POST'])
def update_ticket_status(ticket_id):
    if not is_logged_in():
        return redirect(url_for('admin.login'))
    ticket = TicketRequest.query.get_or_404(ticket_id)
    new_status = request.form.get('status', 'pending')
    ticket.status = new_status
    db.session.commit()
    flash('Durum güncellendi', 'success')
    return redirect(url_for('admin.tickets'))
