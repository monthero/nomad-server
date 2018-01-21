# encoding: utf-8

from json import loads
from os import makedirs, remove, walk, listdir
from os.path import join, exists
import arrow
from PIL import Image
from flask import jsonify, request, render_template, redirect, url_for
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
from httpagentparser import simple_detect
# from livereload import Server
from sqlalchemy import or_, exc, cast, type_coerce, String, JSON
from sqlalchemy.orm.attributes import flag_modified
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room
from db_models import main as db_inserts, db, Partner, Report, ReportSubCategory, ReportCategory, Temple, \
    TempleCategory, User, ShopItem, app, Event, Mission, Tribe, CityZone, Achievement, FriendRequest
from math import ceil
from geopy import Point
from geopy.distance import vincenty
from sqlalchemy import cast, type_coerce, String, JSON

login_manager = LoginManager()
login_manager.init_app(app)
db.init_app(app)

ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']
REPORT_IMAGES_FOLDER = "static\\report_imgs"
PARTNER_UPLOAD_FOLDER = "static\\partner_logos"
USER_IMAGES_FOLDER = "static\\user_images"
TEMPLE_IMG_FOLDER = "static\\temple_images"

# server = Server(app.wsgi_app)
# cors = CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, async_mode=None)


def from_app(req):
    user_agent = simple_detect(req.headers['User-Agent'])
    if "android" in user_agent[0].lower() or "ios" in user_agent[0].lower():
        return True
    return False


@app.template_filter('humanize_date')
def humanize_date(s):
    date = arrow.get(s).to('utc')
    return date.humanize(locale='pt_PT')


@app.template_filter('limit_translator')
def limit_translator(s):
    if s:
        dur = dict(day="dia", month="mês", year="ano")
        return str(s['quantity']) + " por " + dur[s['duration']]
    else:
        return ""


@app.template_filter('rank_translator')
def rank_translator_filter(s):
    ranks = dict(
        chief='chefe',
        healer='curandeiro',
        shaman='xamã',
        hunter='caçador',
        warrior='guerreiro',
        scout='batedor',
        colector='coletor',
        bard='bardo'
    )
    return ranks[s]


@app.template_filter('report_state_translator')
def report_state_translator(s):
    state = int(s)
    if state == 0:
        return "pan_tool", "À espera", "waiting"
    elif state == 1:
        return "find_in_page", "Em análise", "waiting"
    elif state == 2:
        return "done", "Resolvida", "waiting"
    else:
        return "call", "Caso especial", "waiting"


@app.template_filter('tribe_translator')
def tribe_translator_filter(s):
    tribes = dict(
        earth="terra", fire="fogo", spirit="espírito", water="água", wind="vento"
    )
    return tribes[s]


@app.template_filter('category_order_by')
def category_order_by(lst, field):
    if field == "name_pt":
        return sorted(lst, key=lambda x: x.name['pt'], reverse=False)
    else:
        return "ver filter"


@app.template_filter('event_dt')
def event_datetime_filter(s):
    date = arrow.get(s).to('utc')
    return date.format('D MMM YYYY', locale='pt').title() + ', ' + date.format('HH:mm')


@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)


@app.before_request
def before_request():
    app.jinja_env.cache = {}


@app.before_first_request
def setup():
    db.create_all()
    db_inserts()


'''
@app.context_processor
def inject_user():
    return dict(user=g.user)
'''


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:8000')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type, Authorization, Content-Length, X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


@app.route('/')
def home():
    if request.method == 'GET':
        return render_template('layout.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')

        exists_username = db.session.query(
            db.session.query(User).filter_by(username=username).exists()).scalar()
        exists_email = db.session.query(
            db.session.query(User).filter_by(email=email).exists()).scalar()

        if exists_username and exists_email:
            return jsonify(dict(code=0, error="Username e email já existem"))
        if exists_username and not exists_email:
            return jsonify(dict(code=0, error="Username já existe"))
        if not exists_username and exists_email:
            return jsonify(dict(code=0, error="Email já existe"))

        new_user = User(un=username,
                        e=email,
                        pw=request.form.get('password'),
                        gender=int(request.form.get('gender')),
                        dob=request.form.get('dob_string'),
                        tribe_id=int(request.form.get('tribe_id')),
                        cz=int(request.form.get('city_zone_id'))
                        )
        db.session.add(new_user)
        db.session.flush()

        if not exists(join(USER_IMAGES_FOLDER, str(new_user.id))):
            makedirs(join(USER_IMAGES_FOLDER, str(new_user.id)))

        if new_user.gender == 1:
            image = Image.open(join(USER_IMAGES_FOLDER, 'female.png')).convert('RGB')
        else:
            image = Image.open(join(USER_IMAGES_FOLDER, 'female.png')).convert('RGB')

        image.save(join(USER_IMAGES_FOLDER, str(new_user.id) + "\\0.jpg"), optimize=True, quality=85,
                   format='JPEG')

        try:
            db.session.commit()
            return jsonify(dict(code=1))
        except exc.SQLAlchemyError:
            return jsonify(dict(code=0, error="Erro no servidor, por favor tente mais tarde"))


@app.route('/am_i_logged_in', methods=['GET'])
def am_i_logged_in():
    if request.method == 'GET' and getattr(current_user, 'id', None) is not None:
        return jsonify(dict(
            code=1,
            user=current_user.to_json(),
            temples=[t.light_json() for t in Temple.query.filter_by(active=True).all()]
        ))
    else:
        return jsonify(dict(code=0))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        credential = request.form.get('credential')
        password = request.form.get('password')
        if not credential and not password:
            return jsonify(dict(code=0, error="empty credential and password"))
        user = db.session.query(User).filter(
            or_(User.username.like(credential), User.email.like(credential))).first()

        if user:
            if user.is_blocked:
                return jsonify(dict(code=0, error="A sua conta está bloqueada"))
            else:
                if user.verify_password(password):
                    user.authenticated = True
                    user.anonymous = False
                    login_user(user, remember=True)
                    return jsonify(dict(code=1, user=user.to_json()))
                    # return jsonify({'code': 1, 'user': user.to_json()})
                else:
                    return jsonify(dict(code=0, error="Password errada"))
        else:
            return jsonify(dict(code=0, error="Não existe conta com esse nome de utilizador ou email"))


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'GET':
        # current_user.authenticated = False
        # logout_user()
        # return redirect(url_for('home'))
        pass
    elif request.method == 'POST' and getattr(current_user, 'id', None) is not None:
        current_user.authenticated = False
        logout_user()
        return jsonify(dict(code=1))
    return jsonify(dict(code=0))


@app.route('/administracao/<string:action>', methods=['GET'])
def admin_area_action(action):
    if request.method == 'GET':
        if action == 'utilizadores':
            return render_template('users.html',
                                   active_users=User.query.filter_by(is_blocked=False).all(),
                                   blocked_users=User.query.filter_by(is_blocked=True).all())
        elif action == 'participacoes':
            return render_template('reports.html',
                                   new_reports=[r.to_json() for r in Report.query.filter_by(state=0).order_by(
                                       Report.created_at.desc()).all()],
                                   active_reports=[r.to_json() for r in Report.query.filter_by(state=1).order_by(
                                       Report.created_at.desc()).all()],
                                   solved_reports=[r.to_json() for r in Report.query.filter_by(state=2).order_by(
                                       Report.created_at.desc()).all()],
                                   special_case_reports=[r.to_json() for r in Report.query.filter_by(state=3).order_by(
                                       Report.created_at.desc()).all()],
                                   report_categories=[rc.to_json() for rc in ReportCategory.query.all()],
                                   )
        elif action == 'loja':
            return render_template('shop.html',
                                   active_shop_items=sorted(
                                       [si.to_json() for si in ShopItem.query.filter_by(active=True).all()],
                                       key=lambda x: x['name']['pt']),
                                   inactive_shop_items=sorted(
                                       [si.to_json() for si in ShopItem.query.filter_by(active=False).all()],
                                       key=lambda x: x['name']['pt'])
                                   )
        elif action == 'templos':
            return render_template('temples.html',
                                   temples=sorted([t.to_json() for t in Temple.query.all()],
                                                  key=lambda x: x['name']['pt']),
                                   temple_categories=sorted([st.to_json() for st in TempleCategory.query.all()],
                                                            key=lambda x: x['name']['pt'])
                                   )
        elif action == 'parceiros':
            return render_template('partners.html',
                                   active_partners=Partner.query.filter_by(active=True).order_by(Partner.name),
                                   inactive_partners=Partner.query.filter_by(active=False).order_by(Partner.name))

        elif action == 'eventos':
            return render_template('events.html')


@app.route('/administracao', methods=['GET'])
def admin_area_users():
    if request.method == 'GET':
        return redirect(url_for('admin_area_action', action='utilizadores'))


@app.route('/get_infomation_to_signup_page', methods=['GET'])
def get_infomation_to_signup_page():
    if request.method == 'GET':
        return jsonify({'res': 1,
                        'tribes': [t.to_json() for t in Tribe.query.all()],
                        'city_zones': [cz.to_json() for cz in CityZone.query.order_by(CityZone.name)]})
    return jsonify({'res': 0})


@app.route('/admin_user_action', methods=['POST'])
def admin_user_action():
    if request.method == 'POST' and getattr(current_user, 'id', None) is not None and current_user.is_admin:
        ids = request.json['ids']
        action = request.json['action']
        if action == 'delete':
            User.query.filter(User.id.in_(ids)).delete()
        elif action == 'block':
            for user in User.query.filter(User.id.in_(ids)).all():
                user.accepted_state = 0
        elif action == 'unblock':
            for user in User.query.filter(User.id.in_(ids)).all():
                user.accepted_state = 1
        elif action == 'accept':
            for user in User.query.filter(User.id.in_(ids)).all():
                user.accepted_state = 1

        try:
            db.session.commit()
            return jsonify({'code': 1, 'action': action})
        except exc.SQLAlchemyError:
            return jsonify({'code': -1, 'action': action})

    return jsonify(dict(code=0))


@app.route('/admin_report_action', methods=['POST'])
def admin_report_action():
    if request.method == 'POST' and getattr(current_user, 'id', None) is not None and current_user.is_admin:
        ids = request.json['ids']
        action = request.json['action']
        if action == 'delete':
            Report.query.filter(Report.id.in_(ids)).delete()
        elif action == 'analize':
            for rep in Report.query.filter(Report.id.in_(ids)).all():
                rep.state = 1
        elif action == 'done':
            for rep in Report.query.filter(Report.id.in_(ids)).all():
                rep.state = 2
        elif action == 'special':
            for rep in Report.query.filter(Report.id.in_(ids)).all():
                rep.state = 3

        try:
            db.session.commit()
            return jsonify({'code': 1, 'action': action})
        except exc.SQLAlchemyError:
            return jsonify({'code': -1, 'action': action})
    return jsonify(dict(code=0))


@app.route('/admin_temple_action', methods=['POST'])
def admin_temple_action():
    if request.method == 'POST' and getattr(current_user, 'id', None) is not None and current_user.is_admin:
        ids = request.json['ids']
        action = request.json['action']

        if action == 'delete':
            for s in Temple.query.filter(Temple.id.in_(ids)).all():
                db.session.delete(s)
        elif action == 'hide':
            for s in Temple.query.filter(Temple.id.in_(ids)).all():
                s.active = False
        elif action == 'show':
            for s in Temple.query.filter(Temple.id.in_(ids)).all():
                s.active = True
        elif action == 'save':
            temple_id = int(request.json['temple_id'])
            temple = Temple.query.get(temple_id)
            temple.name = request.json['name']
            temple.description = request.json['description']
            lat, lng = request.json['location'].split(", ")
            temple.geometry['location'] = dict(lat=format(round(float(lat), 6), '.6f'),
                                               lng=format(round(float(lng), 6), '.6f'))
            flag_modified(temple, "geometry")
            temple.categories = []
            for cat_id in ids:
                temple.categories.append(TempleCategory.query.get(int(cat_id)))

        try:
            db.session.commit()
            return jsonify({'code': 1, 'action': action})
        except exc.SQLAlchemyError:
            return jsonify({'code': -1, 'action': action})

    return jsonify(dict(code=0))


@app.route('/save_new_temple', methods=['POST'])
def save_new_spot():
    if request.method == 'POST' and getattr(current_user, 'id', None) is not None and current_user.is_admin:
        if request.json['name'] and request.json['desc'] and request.json['lat'] and request.json['lng']:
            # AQUI NÃO VAI FUNCIONAR POR CAUSA DO NOME E DA DESCRIÇÃO, VER ISTO!! TÊM QUE SER JSON
            new_temple = Temple(name=request.json['name'],
                                desc=request.json['desc'],
                                geometry=dict(location=dict(lat=format(float(request.json['lat']), '.6f'),
                                                            lng=format(float(request.json['lng']), '.6f'))),
                                types=request.json['types']
                                )
            db.session.add(new_temple)
            try:
                db.session.commit()
                return jsonify(dict(code=1))
            except exc.SQLAlchemyError:
                return jsonify(dict(code=-1))

    return jsonify(dict(code=0))


@app.route('/get_new_event_info', methods=['GET'])
def get_new_event_info():
    if request.method == 'GET' and getattr(current_user, 'id', None) is not None and current_user.is_admin:
        missions = Mission.query.filter_by(is_daily=False).all()
        shop_items = ShopItem.query.filter_by(active=True).all()
        return jsonify(
            {'code': 1, 'missions': [m.to_json() for m in missions], 'shop_items': [si.to_json() for si in shop_items]})
    return jsonify(dict(code=0))


def next_image_name(list):
    max = -1
    for name in list:
        current = int(name.split(".")[0])
        if current > max:
            max = current
    return max + 1


@app.route('/admin_temple_image_action/<int:temple_id>', methods=['POST'])
def admin_temple_image_action(temple_id):
    if request.method == 'POST' and getattr(current_user, 'id', None) is not None and current_user.is_admin:
        action = request.form.get('action')
        temple = Temple.query.get(temple_id)

        if temple:
            if action == 'delete':
                list = loads(request.form.get('list'))
                for item in list:
                    try:
                        remove(join(TEMPLE_IMG_FOLDER, str(temple_id) + "\\" + item))
                    except OSError:
                        print("erro a apagar ficheiro " + TEMPLE_IMG_FOLDER + "\\" + str(temple_id) + "\\" + item)

                try:
                    db.session.commit()
                    return jsonify({'code': 1, 'action': action, 'removed': list})
                except exc.SQLAlchemyError:
                    return jsonify({'code': -1, 'action': action})

            elif action == 'add':
                if not exists(join(TEMPLE_IMG_FOLDER, str(temple_id))):
                    makedirs(join(TEMPLE_IMG_FOLDER, str(temple_id)))

                files = request.files.getlist('pic')
                if len(files) > 0:
                    count = 0
                    next = next_image_name(temple.get_images())
                    for file in files:
                        if allowed_file(file.filename):
                            image = Image.open(file)
                            width, height = image.size
                            if width >= height and width > 650:
                                image = image.resize((600, int(600.0 * height * 1.0 / width * 1.0)),
                                                     Image.ANTIALIAS)
                            elif height > width and height > 650:
                                image = image.resize((int(600.0 * width * 1.0 / height * 1.0), 600),
                                                     Image.ANTIALIAS)

                            filename = str(next + count) + "." + file.filename.rsplit('.', 1)[1].lower()
                            image.save(join(TEMPLE_IMG_FOLDER, str(temple_id) + "\\" + filename),
                                       optimize=True,
                                       quality=70)

                            count += 1
                try:
                    db.session.commit()
                    return jsonify(dict(code=1, action=action, images=temple.images))
                except exc.SQLAlchemyError:
                    return jsonify(dict(code=-1, action=action))

    return jsonify(dict(code=0))


@app.route('/admin_partner_action', methods=['POST'])
def admin_partner_action():
    if request.method == 'POST' and getattr(current_user, 'id', None) is not None and current_user.is_admin:
        ids = request.json['ids']
        action = request.json['action']

        if action == 'delete':
            for p in Partner.query.filter(Partner.id.in_(ids)).all():
                db.session.delete(p)
        elif action == 'hide':
            for p in Partner.query.filter(Partner.id.in_(ids)).all():
                p.active = False
        elif action == 'show':
            for p in Partner.query.filter(Partner.id.in_(ids)).all():
                p.active = True
        try:
            db.session.commit()
            return jsonify({'code': 1, 'action': action})
        except exc.SQLAlchemyError:
            return jsonify({'code': -1, 'action': action})

    return jsonify(dict(code=0))


@app.route('/get_partner_info/<int:partner_id>', methods=['GET'])
def get_partner_info(partner_id):
    if request.method == 'GET' and getattr(current_user, 'id', None) is not None and current_user.is_admin:
        partner = Partner.query.get(partner_id)
        if partner:
            return jsonify({'code': 1, 'partner': partner.to_json()})
        else:
            return jsonify(dict(code=0))
    return jsonify(dict(code=-1))


@app.route('/get_temple_categories', methods=['GET'])
def get_temple_categories():
    if request.method == 'GET' and getattr(current_user, 'id', None) is not None and current_user.is_admin:
        return jsonify(dict(code=1,
                            temple_categories=sorted([t.to_json for t in TempleCategory.query.all()],
                                                     key=lambda x: x['name']['pt'])))

    return jsonify(dict(code=-1))


@app.route('/get_partner_list', methods=['GET'])
def get_partner_list():
    if request.method == 'GET' and getattr(current_user, 'id', None) is not None and current_user.is_admin:
        return jsonify(dict(code=1,
                            partners=[p.to_json() for p in
                                      Partner.query.filter_by(active=True).order_by(Partner.name)]))

    return jsonify(dict(code=-1))


@app.route('/get_temple_info/<int:temple_id>', methods=['GET'])
def get_temple_info(temple_id):
    if request.method == 'GET' and getattr(current_user, 'id', None) is not None and current_user.is_admin:
        temple = Temple.query.get(temple_id)
        if temple:
            return jsonify(dict(code=1,
                                temple=temple.to_json(),
                                temple_categories=sorted([st.to_json() for st in TempleCategory.query.all()],
                                                         key=lambda d: d['name']['pt'])
                                ))
        else:
            return jsonify(dict(code=0))
    return jsonify(dict(code=-1))


@app.route('/edit_partner_info/<int:partner_id>', methods=['POST'])
def edit_partner_info(partner_id):
    if request.method == 'POST' and getattr(current_user, 'id', None) is not None and current_user.is_admin:
        partner = Partner.query.get(partner_id)
        if partner:
            partner.name = request.form.get('name')
            partner.address = None if request.form.get('address') == 'null' else request.form.get('address')
            partner.url = None if request.form.get('url') == 'null' else request.form.get('url')
            partner.description = None if request.form.get('desc') == 'null' else request.form.get('desc')
            partner.gps_location = loads(request.form.get('gps'))

            imtype = request.form.get('imgtype')
            src = request.form.get('src')

            if partner.logo_img['type'] == imtype:
                if imtype == 'url' or imtype == 'none':
                    partner.logo_img = {'type': imtype, 'src': src}
                elif imtype == 'static':
                    if src == 'filechange':
                        files = request.files.getlist('pic')
                        if len(files) > 0:
                            file = files[0]
                            if allowed_file(file.filename):
                                image = Image.open(file)
                                width, height = image.size
                                image = image.resize((400, int(400.0 * height * 1.0 / width * 1.0)),
                                                     Image.ANTIALIAS).convert('RGB')
                                image.save(join(PARTNER_UPLOAD_FOLDER, str(partner.id) + ".jpg"),
                                           optimize=True,
                                           quality=70,
                                           format='JPEG')

            else:
                if imtype == 'url' or imtype == 'none':
                    partner.logo_img = {'type': imtype, 'src': src}
                else:
                    files = request.files.getlist('pic')
                    if len(files) > 0:
                        file = files[0]
                        if allowed_file(file.filename):
                            image = Image.open(file)
                            width, height = image.size
                            image = image.resize((400, int(400.0 * height * 1.0 / width * 1.0)),
                                                 Image.ANTIALIAS).convert('RGB')
                            image.save(join(PARTNER_UPLOAD_FOLDER, str(partner.id) + ".jpg"),
                                       optimize=True,
                                       quality=70,
                                       format='JPEG')

                    partner.logo_img = {'type': 'static', 'src': str(partner.id) + ".jpg"}

            db.session.commit()
            return jsonify(dict(code=1))
        else:
            return jsonify(dict(code=0))
    return jsonify(dict(code=-1))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/add_partner', methods=['POST'])
def add_partner():
    if request.method == 'POST' and getattr(current_user, 'id', None) is not None and current_user.is_admin:
        imtype = request.form.get('imgtype')

        new_partner = Partner(
            name=request.form.get('name'),
            logo=None,
            add=None if request.form.get('address') == 'null' else request.form.get('address'),
            gps=loads(request.form.get('gps')),
            url=None if request.form.get('url') == 'null' else request.form.get('url'),
            desc=None if request.form.get('desc') == 'null' else request.form.get('desc')
        )

        db.session.add(new_partner)
        db.session.flush()

        logo = {'type': imtype, 'src': ''}
        if imtype == 'url':
            logo['src'] = request.form.get('img_url')
        elif imtype == 'static':
            files = request.files.getlist('pic')
            if len(files) > 0:
                file = files[0]
                if allowed_file(file.filename):
                    image = Image.open(file)
                    width, height = image.size
                    image = image.resize((400, int(400.0 * height * 1.0 / width * 1.0)), Image.ANTIALIAS).convert('RGB')
                    image.save(join(PARTNER_UPLOAD_FOLDER, str(new_partner.id) + ".jpg"),
                               optimize=True,
                               quality=70,
                               format='JPEG')
                    logo['src'] = str(new_partner.id) + ".jpg"
            else:
                logo['src'] = 'no_pic.jpg'

        new_partner.logo_img = logo

        db.session.commit()
        return jsonify(dict(code=1, partner=new_partner.to_json()))

    return jsonify(dict(code=-1))


@app.route('/report_submission', methods=['POST'])
@login_required
def report_submission():
    if request.method == 'POST' and getattr(current_user, 'id', None) is not None:
        new_report = Report(loc=loads(request.form.get('location')),
                            rep_category=request.form.get('cat_id', type=int),
                            uid=current_user.id,
                            desc=request.form.get('description'),
                            is_remote=request.form.get('remote'))
        db.session.add(new_report)
        db.session.flush()

        '''
        now = arrow.utcnow()
        rep_loc = Point(latitude=float(format(float(new_report.gps_location['lat']), '.6f')),
                        longitude=float(format(float(new_report.gps_location['lng']), '.6f')))

        near_temples = []
        for t in Temple.query.all():
            temple_loc = Point(latitude=float(format(float(t.geometry['location']['lat']), '.6f')),
                               longitude=float(format(float(t.geometry['location']['lng']), '.6f')))
            dist = vincenty(rep_loc, temple_loc).kilometers * 1000
            if dist <= 500:
                near_temples.append(dict(temple=t.id, dist=dist))

        near_temples = sorted(near_temples, key=lambda x: x['dist'], reverse=False)
        if len(near_temples) > 0:
            current_user.activity_log.insert(0, dict(
                action='report',
                rep_id=new_report.id,
                date=str(now.datetime),
                remote=is_remote,
                near=dict(
                    id=int(near_temples[0]['temple']),
                    name=Temple.query.get(int(near_temples[0]['temple'])).name['pt'])
            ))
        else:
            current_user.activity_log.insert(0, dict(action='report',
                                                     rep_id=new_report.id,
                                                     remote=is_remote,
                                                     date=str(now.datetime),
                                                     near=None
                                                     ))

        flag_modified(current_user, 'activity_log')
        '''
        files = request.files.getlist('pic')
        if len(files) > 0:
            if not exists(join(REPORT_IMAGES_FOLDER, str(new_report.id))):
                makedirs(join(REPORT_IMAGES_FOLDER, str(new_report.id)))
            count = 0
            for file in files:
                if allowed_file(file.filename):
                    file.seek(0, 2)
                    filesize = int(file.tell())
                    image = Image.open(file)
                    if filesize > 120000:
                        width, height = image.size
                        if width > 1000:
                            image = image.resize((600, int(600.0 * height * 1.0 / width * 1.0)), Image.ANTIALIAS)

                    image.save(join(REPORT_IMAGES_FOLDER, str(new_report.id) + "\\" + str(count) + ".jpg"),
                               optimize=True,
                               quality=70,
                               format='JPEG')

                    count += 1

            new_report.images = count
        db.session.commit()

        return jsonify(dict(code=1, report=new_report.to_json()))
    return jsonify(dict(code=-1))


@app.route('/user_friendlist_action', methods=['POST'])
def user_friendlist_action():
    if request.method == 'POST' and getattr(current_user, 'id', None) is not None:
        action = request.json['action']
        if 'user_id' in request.json:
            user_id = int(request.json['user_id'])
            if action == 'remove_friend':
                req = FriendRequest.query.filter_by(inviter_id=user_id).filter_by(invitee_id=current_user.id).first()
                if req:
                    db.session.delete(req)
                    db.session.commit()
                    return jsonify(dict(code=1))
                req = FriendRequest.query.filter_by(inviter_id=current_user.id).filter_by(invitee_id=user_id).first()
                if req:
                    db.session.delete(req)
                    db.session.commit()
                    return jsonify(dict(code=1))
                else:
                    return jsonify(dict(code=0))

                pass
            elif action == 'add_friend':
                req = FriendRequest.query.filter_by(inviter_id=user_id).filter_by(invitee_id=current_user.id).first()
                if req:
                    req.is_accepted = True
                    db.session.commit()
                    return jsonify(dict(code=2, req=dict(id=req.id,
                                                         sent_at=arrow.get(req.sent_at).to('utc').humanize(locale='pt'),
                                                         ), me=current_user.to_chat_json()))
                req = FriendRequest.query.filter_by(inviter_id=current_user.id).filter_by(invitee_id=user_id).first()
                if req:
                    return jsonify(dict(code=3))
                new_req = FriendRequest(src=current_user.id, dest=user_id)
                db.session.add(new_req)
                db.session.flush()
                new_req_id = new_req.id
                db.session.commit()
                return jsonify(dict(code=1))
            elif action == 'accept_friend' or action == 'reject_friend':
                req = FriendRequest.query.filter_by(inviter_id=user_id).filter_by(invitee_id=current_user.id).first()
                if req:
                    if action == 'accept_friend':
                        req.is_accepted = True
                        # db.session.commit()
                        return jsonify(dict(code=1, me=current_user.to_chat_json()))
                    elif action == 'reject_friend':
                        db.session.delete(req)
                        db.session.commit()
                        return jsonify(dict(code=1))
                else:
                    return jsonify(dict(code=0))
            elif action == 'cancel_invite':
                req = FriendRequest.query.filter_by(inviter_id=current_user.id).filter_by(invitee_id=user_id).first()
                if req:
                    db.session.delete(req)
                    db.session.commit()
                    return jsonify(dict(code=1))
                else:
                    return jsonify(dict(code=0))
        else:
            req = FriendRequest.query.get(int(request.json['req_id']))
            if req:
                if action == 'accept':
                    req.is_accepted = True
                else:
                    db.session.delete(req)
                db.session.commit()
                return jsonify({'code': 1})
            else:
                return jsonify(dict(code=0))
    return jsonify(dict(code=-1))


@app.route('/user_temple_action', methods=['POST'])
def user_temple_action():
    if request.method == 'POST' and getattr(current_user, 'id', None) is not None:
        action = request.json['action']
        temple = Temple.query.get(int(request.json['temple_id']))
        if temple:
            res = current_user.execute_temple_action(temple=temple,
                                                     action=request.json['action'],
                                                     pos=request.json['pos'])

            flag_modified(current_user, 'inventory')
            flag_modified(current_user, 'actions')
            flag_modified(current_user, 'progress')
            flag_modified(temple, 'tribe_points')

            db.session.commit()
            return jsonify(dict(code=1, action_result=res))
        return jsonify(dict(code=0))
    return jsonify(dict(code=-1))


def generate_rankings():
    pop = [{'user': u.to_chat_json(), 'points': u.get_ranking_points()} for u in
           User.query.filter_by(is_blocked=False).all()]

    pop = sorted(pop, key=lambda x: x['user']['name'].lower(), reverse=False)
    # general_rank = sorted(info, key=lambda x: (x['points']['total'], x['user']['name']), reverse=True)
    general_rank = sorted(pop, key=lambda x: x['points']['total'], reverse=True)
    gr = [{'user': x['user'], 'points': x['points']['total']} for x in general_rank]
    weekly_rank = sorted(pop, key=lambda x: x['points']['this_week'], reverse=True)
    wr = [{'user': x['user'], 'points': x['points']['this_week']} for x in weekly_rank]
    tribe_points = {'earth': {'points': 0, 'temples': 0},
                    'fire': {'points': 0, 'temples': 0},
                    'spirit': {'points': 0, 'temples': 0},
                    'water': {'points': 0, 'temples': 0},
                    'wind': {'points': 0, 'temples': 0}}

    for temple in Temple.query.filter_by(active=True).all():
        for elem, points in temple.tribe_points.items():
            tribe_points[elem]['points'] += points
        conq = temple.current_conqueror()
        if conq != 'neutral':
            tribe_points[conq]['temples'] += 1

    tribes_rank = [{'tribe': elem, 'info': value} for elem, value in tribe_points.items()]
    tr = sorted(tribes_rank, key=lambda x: (x['info']['points'], x['info']['temples']), reverse=True)

    # my_gen_rank_index = next(i for (i, d) in enumerate(general_rank) if d['user']['id'] == user_id)
    # my_weekly_rank_index = next(i for (i, d) in enumerate(weekly_rank) if d['user']['id'] == user_id)

    lp = len(pop) - 1
    ranks = [
        {'len': 1, 'filled': 1, 'rank': 'chief'},
        {'len': int(ceil(lp * 0.02)), 'filled': 0, 'rank': 'shaman'},
        {'len': int(ceil(lp * 0.07)), 'filled': 0, 'rank': 'healer'},
        {'len': int(ceil(lp * 0.11)), 'filled': 0, 'rank': 'hunter'},
        {'len': int(ceil(lp * 0.15)), 'filled': 0, 'rank': 'warrior'},
        {'len': int(ceil(lp * 0.18)), 'filled': 0, 'rank': 'scout'},
        {'len': int(ceil(lp * 0.21)), 'filled': 0, 'rank': 'colector'},
        {'len': int(ceil(lp * 0.26)), 'filled': 0, 'rank': 'bard'}
    ]

    ranks2 = [
        {'len': 1, 'filled': 1, 'rank': 'chief'},
        {'len': int(ceil(lp * 0.02)), 'filled': 0, 'rank': 'shaman'},
        {'len': int(ceil(lp * 0.07)), 'filled': 0, 'rank': 'healer'},
        {'len': int(ceil(lp * 0.11)), 'filled': 0, 'rank': 'hunter'},
        {'len': int(ceil(lp * 0.15)), 'filled': 0, 'rank': 'warrior'},
        {'len': int(ceil(lp * 0.18)), 'filled': 0, 'rank': 'scout'},
        {'len': int(ceil(lp * 0.21)), 'filled': 0, 'rank': 'colector'},
        {'len': int(ceil(lp * 0.26)), 'filled': 0, 'rank': 'bard'}
    ]

    if lp > 0:
        gr[0]['rank'] = 'bard' if gr[0]['points'] == 0 else 'chief'
        wr[0]['rank'] = 'bard' if wr[0]['points'] == 0 else 'chief'
    if lp > 1:
        curr_rank_index = 1
        for i in range(1, len(gr)):
            if gr[i]['points'] == 0:
                gr[i]['rank'] = 'bard'
                ranks[-1]['filled'] += 1
            else:
                if ranks[curr_rank_index]['rank'] != 'bard' and (
                        ranks[curr_rank_index]['filled'] < ranks[curr_rank_index]['len']):
                    gr[i]['rank'] = ranks[curr_rank_index]['rank']
                    ranks[curr_rank_index]['filled'] += 1
                elif ranks[curr_rank_index]['rank'] != 'bard' and (
                        ranks[curr_rank_index]['filled'] == ranks[curr_rank_index]['len']):
                    curr_rank_index += 1
                    gr[i]['rank'] = ranks[curr_rank_index]['rank']
                    ranks[curr_rank_index]['filled'] += 1
                else:
                    gr[i]['rank'] = 'bard'
                    ranks[-1]['filled'] += 1

        curr_rank_index = 1
        for i in range(1, len(gr)):
            if wr[i]['points'] == 0:
                wr[i]['rank'] = 'bard'
                ranks2[-1]['filled'] += 1
            else:
                if ranks2[curr_rank_index]['rank'] != 'bard' and (
                        ranks2[curr_rank_index]['filled'] < ranks2[curr_rank_index]['len']):
                    wr[i]['rank'] = ranks2[curr_rank_index]['rank']
                    ranks2[curr_rank_index]['filled'] += 1
                elif ranks2[curr_rank_index]['rank'] != 'bard' and (
                        ranks2[curr_rank_index]['filled'] == ranks2[curr_rank_index]['len']):
                    curr_rank_index += 1
                    wr[i]['rank'] = ranks2[curr_rank_index]['rank']
                    ranks2[curr_rank_index]['filled'] += 1
                else:
                    wr[i]['rank'] = 'bard'
                    ranks2[-1]['filled'] += 1

    # return gr, wr, tr, my_gen_rank_index, my_weekly_rank_index
    return gr, wr, tr, len(Temple.query.filter_by(active=True).all())


@app.route('/get_shopitem_info/<int:item_id>', methods=['GET'])
def get_shopitem_info(item_id):
    if request.method == "GET":
        item = ShopItem.query.get(item_id)
        if item:
            pass
    return jsonify(dict(code=-1))


@app.route('/get_app_view', methods=['GET'])
def get_app_view():
    if request.method == 'GET':
        info = loads(list(request.args)[0])
        action = info['action']
        address = ""
        if 'address' in info:
            address = info['address']
        if action == 'shop_item_page':
            item = ShopItem.query.get(int(info['item_id']))
            if item:
                return render_template("app/shop_item_page.html", address=address, item=item)
            else:
                return jsonify(dict(code=0))
        elif action == 'new_report_page':
            return render_template("app/new_report_window.html",
                                   report_categories=ReportCategory.query.order_by(
                                       cast(ReportCategory.name['pt'], String)).all())
        elif action == 'report_page':
            report = Report.query.get(int(info['report_id']))
            if report:
                return render_template("app/report_page.html", report=report.to_json(), address=address)
            else:
                return jsonify(dict(code=0))
        elif action == 'shop':
            return render_template("app/shop.html", items=ShopItem.query.filter_by(active=True).order_by(
                cast(ShopItem.name['pt'], String)).all(), address=address)
        elif action == 'reports':
            return render_template("app/reports.html",
                                   waiting=current_user.reports_sent.filter_by(state=0).order_by(
                                       Report.created_at.desc()).all(),
                                   analysis=current_user.reports_sent.filter_by(state=1).order_by(
                                       Report.created_at.desc()).all(),
                                   solved=current_user.reports_sent.filter_by(state=2).order_by(
                                       Report.created_at.desc()).all(),
                                   special=current_user.reports_sent.filter_by(state=3).order_by(
                                       Report.created_at.desc()).all()
                                   )
        elif action == 'rankings':
            gr, wr, tr, tt = generate_rankings()
            return render_template("app/rankings.html", general=gr, weekly=wr, tribes=tr, total_temples=tt,
                                   address=address)
        elif action == 'challenges':
            return render_template("app/challenges.html")
        elif action == 'profile':
            user = User.query.get(int(info['user_id']))
            if user:
                is_linked = info['linked']
                fl = current_user.get_friend_list_status() if current_user.id == user.id else dict(
                    friends=user.get_friend_list_status()['friends'])
                fs = None if current_user.id == user.id else current_user.is_friend_and_get_friends_in_common(
                    user=user)
                msgs = current_user.get_internal_messages_information() if current_user.id == user.id else []
                to_nl = current_user.to_next_level() if current_user.id == user.id else None
                return render_template("app/profile.html",
                                       address=address,
                                       user=user,
                                       friend_list=fl,
                                       stats=user.get_profile_stats(),
                                       friend_status=fs,
                                       messages=msgs,
                                       is_linked=is_linked,
                                       bio=user.to_chat_json(),
                                       to_next_level=to_nl,
                                       search_users=[u.to_chat_json() for u in
                                                     User.query.filter_by(is_blocked=False).order_by(
                                                         User.username).all() if u.id != current_user.id]
                                       )

            else:
                return jsonify(dict(code=0))
        elif action == 'temple':
            temple = Temple.query.get(int(info['temple_id']))
            if temple:
                res = current_user.execute_temple_action(temple=temple,
                                                         action='visit',
                                                         pos=info['pos'])

                flag_modified(current_user, 'inventory')
                flag_modified(current_user, 'actions')
                flag_modified(current_user, 'progress')
                flag_modified(temple, 'tribe_points')

                db.session.commit()
                # return jsonify(dict(code=1, action_result=res))
                return render_template("app/temple.html",
                                       address=address,
                                       temple=temple.to_json(),
                                       in_range=res['in_range']
                                       )
            return jsonify(dict(code=0))

    else:
        return jsonify(dict(code=-1))


@app.route('/testes', methods=['GET', 'POST'])
def testes():
    # from langdetect import detect, detect_langs
    # print detect()
    # print detect_langs()
    '''
    import random as r
    temples_ids = [t.id for t in Temple.query.filter_by(active=True).all()]
    uids = [1, 2, 3, 4, 5, 6]
    for i in range(0, 3):
        user = User.query.get(int(r.choice(uids)))
        temple = Temple.query.get(int(r.choice(temples_ids)))
        user.execute_temple_action(temple=temple, action="visit", pos=temple.geometry['location'])
        user.execute_temple_action(temple=temple, action="collect", pos=temple.geometry['location'])
        user.execute_temple_action(temple=temple, action="tribute", pos=temple.geometry['location'])
    '''

    return jsonify("ok")


# connect socket
@socketio.on('connect', namespace='/nomad')
def socket_connect():
    if getattr(current_user, 'id', None) is not None:
        print(str(request.sid) + " -> " + current_user.username + " connected")
        emit('chat', {'channel': 'general', 'text': 'hey guys', 'time': str(arrow.utcnow().datetime),
                      'user': User.query.get(3).to_chat_json()}, broadcast=True)
    else:
        print(str(request.sid) + " -> unknown connected")
    return


# disconnect socket
@socketio.on('disconnect', namespace='/nomad')
def socket_disconnect():
    if getattr(current_user, 'id', None) is not None:
        print(str(request.sid) + " -> " + current_user.username + " disconnected")
    else:
        print('unknown user disconnected')


if __name__ == '__main__':
    '''
    server.watch('static/css/')
    server.watch('static/js')
    server.watch('templates/')
    server.serve(host='localhost', port=5050, debug=True, open_url=True)
    '''
    app.run(host='0.0.0.0', port=5050, use_reloader=True, debug=True)
    # app.run(host='0.0.0.0', port=5050, use_reloader=True, debug=True, extra_files=extra_files)
    # socketio.run(app, host='0.0.0.0', port=5050, use_reloader=True, debug=True)
