from app import create_app
from models import db, Event, Category
from datetime import datetime, timedelta

app = create_app()


def ensure_categories(names):
    out = []
    for name in names:
        cat = Category.query.filter_by(name=name).first()
        if not cat:
            cat = Category(name=name)
            db.session.add(cat)
        out.append(cat)
    return out


with app.app_context():
    db.drop_all()
    db.create_all()

    base = datetime.utcnow()
    events_data = [
        {
            'title': 'Genç Sanatçılar Karma Sergisi',
            'description': (
                'Genç ressam ve heykeltıraşların ortak seçkisi; dijital işler '
                've klasik teknikler bir arada.'
            ),
            'location': 'Kültür ve Sanat Merkezi, Çankaya',
            'days': 3,
            'hours': 18,
            'categories': ['Sergi', 'Görsel Sanatlar'],
            'image': (
                'https://images.unsplash.com/photo-1526498460520-4c246339dccb'
                '?auto=format&fit=crop&w=900&q=80'
            )
        },
        {
            'title': 'Cumhuriyet Tiyatro Gösterimi',
            'description': (
                'Kurtuluş dönemi hikayelerini modern sahne diliyle anlatan '
                'özel oyun.'
            ),
            'location': 'Şehir Tiyatrosu, Altındağ',
            'days': 5,
            'hours': 20,
            'categories': ['Tiyatro'],
            'image': (
                'https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91'
                '?auto=format&fit=crop&w=900&q=80'
            )
        },
        {
            'title': 'Senfonik Konser: Güneşin Çocukları',
            'description': (
                'Ankara Senfoni Orkestrası ve konuk solistlerle film '
                'müzikleri gecesi.'
            ),
            'location': 'CSO Ada Ankara',
            'days': 7,
            'hours': 21,
            'categories': ['Konser', 'Klasik'],
            'image': (
                'https://images.unsplash.com/photo-1454922915609-78549ad709bb'
                '?auto=format&fit=crop&w=900&q=80'
            )
        },
        {
            'title': 'Çocuklar İçin Masal Atölyesi',
            'description': (
                'Yaratıcı drama ve hikaye anlatımıyla çocuklara özel masal '
                'atölyesi.'
            ),
            'location': 'Kent Kütüphanesi, Keçiören',
            'days': 2,
            'hours': 11,
            'categories': ['Atölye', 'Çocuk'],
            'image': (
                'https://images.unsplash.com/photo-1509062522246-3755977927d7'
                '?auto=format&fit=crop&w=900&q=80'
            )
        },
        {
            'title': 'Dijital Sanat ve NFT Paneli',
            'description': (
                'Küratörler ve sanatçılarla NFT piyasası, etik ve '
                'sürdürülebilirlik üzerine panel.'
            ),
            'location': 'Tekmer Sahne, Bilkent',
            'days': 9,
            'hours': 18,
            'categories': ['Panel', 'Dijital Sanat'],
            'image': (
                'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee'
                '?auto=format&fit=crop&w=900&q=80'
            )
        },
        {
            'title': 'Açık Hava Caz Gecesi',
            'description': (
                'Yerel caz topluluklarıyla açık hava konseri; piknik alanı ve '
                'street food köşesi.'
            ),
            'location': 'Seğmenler Parkı',
            'days': 12,
            'hours': 20,
            'categories': ['Konser', 'Caz'],
            'image': (
                'https://images.unsplash.com/photo-1508216310972-bb4c22f19a2f'
                '?auto=format&fit=crop&w=900&q=80'
            )
        },
        {
            'title': 'Fotoğraf Yürüyüşü: Ankara Sokakları',
            'description': (
                'Şehirde iki saatlik fotoğraf yürüyüşü ve temel kompozisyon '
                'eğitimi.'
            ),
            'location': 'Ulus Meydanı buluşma noktası',
            'days': 4,
            'hours': 10,
            'categories': ['Atölye', 'Fotoğraf'],
            'image': (
                'https://images.unsplash.com/photo-1489515217757-5fd1be406fef'
                '?auto=format&fit=crop&w=900&q=80'
            )
        },
        {
            'title': 'Modern Dans Gecesi',
            'description': (
                'Üniversite dans topluluklarının modern dans koreografileri ve '
                'ışık gösterisi.'
            ),
            'location': 'ATO Congresium',
            'days': 8,
            'hours': 19,
            'categories': ['Dans', 'Gösteri'],
            'image': (
                'https://images.unsplash.com/photo-1508214928778-e7077e3cc04e'
                '?auto=format&fit=crop&w=900&q=80'
            )
        },
        {
            'title': 'Ankara Film Geceleri: Bağımsız Kısa Filmler',
            'description': (
                'Seçili kısa filmler gösterimi ve yönetmenlerle söyleşi.'
            ),
            'location': 'Büyülü Fener Kızılay',
            'days': 6,
            'hours': 20,
            'categories': ['Film', 'Söyleşi'],
            'image': (
                'https://images.unsplash.com/photo-1464375117522-1311d6a5b81f'
                '?auto=format&fit=crop&w=900&q=80'
            )
        },
        {
            'title': 'Şehirden İlham Alan İllüstrasyon',
            'description': (
                'İllüstratörlerle yaratıcı çizim atölyesi; malzemeler mekanda '
                'sağlanır.'
            ),
            'location': 'Sanatçılar Sokağı Atölye',
            'days': 10,
            'hours': 14,
            'categories': ['Atölye', 'İllüstrasyon'],
            'image': (
                'https://images.unsplash.com/photo-1503602642458-232111445657'
                '?auto=format&fit=crop&w=900&q=80'
            )
        }
    ]

    for data in events_data:
        cats = ensure_categories(data['categories'])
        ev = Event(
            title=data['title'],
            description=data['description'],
            location=data['location'],
            start_time=base + timedelta(
                days=data['days'],
                hours=data['hours']
            ),
            end_time=base + timedelta(
                days=data['days'],
                hours=data['hours'] + 2
            ),
            image_url=data['image']
        )
        ev.categories.extend(cats)
        db.session.add(ev)

    db.session.commit()
    print('Sample events created (10 items).')
