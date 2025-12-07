from flask import Blueprint, render_template, request, current_app, jsonify, redirect, url_for, flash
from models import db, Event, Category, TicketRequest
from datetime import datetime

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    # category filter
    cat = request.args.get('category')
    if cat:
        events = Event.query.join(Event.categories).filter(Category.name == cat).order_by(Event.start_time).all()
    else:
        events = Event.query.order_by(Event.start_time).all()
    categories = Category.query.order_by(Category.name).all()
    return render_template('index.html', events=events, categories=categories, selected_category=cat)


@main_bp.route('/event/<int:event_id>')
def event_detail(event_id):
    ev = Event.query.get_or_404(event_id)
    return render_template('event.html', event=ev)


@main_bp.route('/about')
def about():
    # simple about page with developers
    developers = [
        {
            'name': 'Damla Yüce',
            'slug': 'damla-yuce',
            'avatar': '/static/img/avatars/damla.svg',
            'role': 'Frontend / UI',
            'bio': 'Kullanıcı deneyimi ve modern web arayüzleri konusunda uzman. React ve modern CSS teknikleriyle etkileyici projeler geliştiriyor.',
            'skills': ['React', 'TypeScript', 'CSS/SCSS', 'Figma', 'UI/UX Design'],
            'github': 'https://github.com/damlayuce',
            'linkedin': 'https://linkedin.com/in/damlayuce'
        },
        {
            'name': 'Zeynep Mertkan',
            'slug': 'zeynep-mertkan',
            'avatar': '/static/img/avatars/zeynep.svg',
            'role': 'Backend / API',
            'bio': 'Flask, Django ve RESTful API tasarımında deneyimli backend geliştirici. Performans ve ölçeklenebilirlik odaklı çözümler üretiyor.',
            'skills': ['Python', 'Flask', 'Django', 'PostgreSQL', 'REST API', 'Docker'],
            'github': 'https://github.com/zeynepmertkan',
            'linkedin': 'https://linkedin.com/in/zeynepmertkan'
        },
        {
            'name': 'Beyza Erdoğan',
            'slug': 'beyza-erdogan',
            'avatar': '/static/img/avatars/beyza.svg',
            'role': 'Database / DevOps',
            'bio': 'Veritabanı yönetimi ve bulut altyapısı konusunda uzman. CI/CD pipeline kurulumu ve sistem güvenliği alanlarında çalışıyor.',
            'skills': ['PostgreSQL', 'MongoDB', 'Docker', 'Kubernetes', 'AWS', 'Linux'],
            'github': 'https://github.com/beyzaerdogan',
            'linkedin': 'https://linkedin.com/in/beyzaerdogan'
        },
    ]
    return render_template('about.html', developers=developers)


@main_bp.route('/developer/<slug>')
def developer_profile(slug):
    developers = [
        {
            'name': 'Damla Yüce',
            'slug': 'damla-yuce',
            'avatar': '/static/img/avatars/damla.svg',
            'role': 'Frontend / UI',
            'bio': 'Kullanıcı deneyimi ve modern web arayüzleri konusunda uzman. React ve modern CSS teknikleriyle etkileyici projeler geliştiriyor.',
            'skills': ['React', 'TypeScript', 'CSS/SCSS', 'Figma', 'UI/UX Design'],
            'github': 'https://github.com/damlayuce',
            'linkedin': 'https://linkedin.com/in/damlayuce'
        },
        {
            'name': 'Zeynep Mertkan',
            'slug': 'zeynep-mertkan',
            'avatar': '/static/img/avatars/zeynep.svg',
            'role': 'Backend / API',
            'bio': 'Flask, Django ve RESTful API tasarımında deneyimli backend geliştirici. Performans ve ölçeklenebilirlik odaklı çözümler üretiyor.',
            'skills': ['Python', 'Flask', 'Django', 'PostgreSQL', 'REST API', 'Docker'],
            'github': 'https://github.com/zeynepmertkan',
            'linkedin': 'https://linkedin.com/in/zeynepmertkan'
        },
        {
            'name': 'Beyza Erdoğan',
            'slug': 'beyza-erdogan',
            'avatar': '/static/img/avatars/beyza.svg',
            'role': 'Database / DevOps',
            'bio': 'Veritabanı yönetimi ve bulut altyapısı konusunda uzman. CI/CD pipeline kurulumu ve sistem güvenliği alanlarında çalışıyor.',
            'skills': ['PostgreSQL', 'MongoDB', 'Docker', 'Kubernetes', 'AWS', 'Linux'],
            'github': 'https://github.com/beyzaerdogan',
            'linkedin': 'https://linkedin.com/in/beyzaerdogan'
        },
    ]
    dev = next((d for d in developers if d['slug'] == slug), None)
    if not dev:
        return render_template('404.html'), 404
    return render_template('developer.html', developer=dev)


@main_bp.route('/api/calendar')
def calendar_api():
    # returns events as JSON for simple calendar integration
    start = request.args.get('start')
    end = request.args.get('end')
    q = Event.query
    if start:
        try:
            s = datetime.fromisoformat(start)
            q = q.filter(Event.start_time >= s)
        except ValueError:
            pass
    if end:
        try:
            e = datetime.fromisoformat(end)
            q = q.filter(Event.start_time <= e)
        except ValueError:
            pass
    events = q.order_by(Event.start_time).all()
    return jsonify([ev.to_dict() for ev in events])


@main_bp.route('/ticket/book', methods=['GET', 'POST'])
def book_ticket():
    if request.method == 'POST':
        event_id = request.form.get('event_id')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        ticket_count = request.form.get('ticket_count', 1, type=int)

        ticket = TicketRequest(
            event_id=event_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            ticket_count=ticket_count
        )
        db.session.add(ticket)
        db.session.commit()
        flash(
            'Bilet talebiniz alındı! Yetkililerimiz en kısa sürede sizinle iletişime geçecektir.',
            'success'
        )
        return redirect(url_for('main.ticket_success'))

    events = Event.query.order_by(Event.start_time).all()
    preselected_id = request.args.get('event_id', type=int)
    return render_template(
        'book_ticket.html',
        events=events,
        preselected_id=preselected_id
    )


@main_bp.route('/ticket/success')
def ticket_success():
    return render_template('ticket_success.html')
