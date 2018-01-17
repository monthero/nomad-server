# encoding: utf-8

import arrow
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from passlib.apps import custom_app_context as pwd_context
from PIL import Image
from os import makedirs, remove, listdir
from os.path import join, exists, isfile
from random import randint, choice
from geopy import Point
from geopy.distance import vincenty
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import cast, type_coerce, String, JSON

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:568600@localhost:5432/nomad_db'
app.config['SECRET_KEY'] = 'secret!'
app.config['CORS_SUPPORTS_CREDENTIALS'] = True

db = SQLAlchemy()

USER_IMAGES_FOLDER = "static\\user_images"
TEMPLE_IMG_FOLDER = "static\\temple_images"

''' CLASSES '''


class Base(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=arrow.utcnow().datetime)
    updated_at = db.Column(
        db.DateTime, default=arrow.utcnow().datetime, onupdate=arrow.utcnow().datetime)


class Achievement(Base):
    __tablename__ = 'achievements'

    name = db.Column(db.JSON, nullable=True)
    description = db.Column(db.JSON, nullable=True)
    reward = db.Column(db.JSON, nullable=True)
    family = db.Column(db.String(40), nullable=True)
    chain_level = db.Column(db.SmallInteger)
    extra_info = db.Column(db.JSON)

    def __init__(self, chain_level, name=None, desc=None, reward=None, family=None, extra=None):
        self.name = name
        self.description = desc
        self.reward = reward
        self.family = family
        self.chain_level = chain_level
        self.extra_info = extra

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'reward': self.reward,
            'family': self.family,
            'chain_level': self.chain_level,
            'extra_info': self.extra_info
        }


class CityZone(Base):
    __tablename__ = 'city_zones'

    name = db.Column(db.String(200))

    users = db.relationship('User', backref='city_zone', lazy='dynamic')

    def __init__(self, name):
        self.name = name

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name
        }


class Partner(Base):
    __tablename__ = 'partners'

    name = db.Column(db.String(100))
    url = db.Column(db.String(255), nullable=True)
    description = db.Column(db.JSON, nullable=False)
    logo_img = db.Column(db.JSON)  # {'type': url/static, 'src': src}
    active = db.Column(db.Boolean)
    address = db.Column(db.String(255))
    gps_location = db.Column(db.JSON)

    # backref 'items'

    def __init__(self, name, logo, add, gps=None, url=None, desc=None, active=True):
        self.name = name
        self.logo_img = logo
        self.url = url
        self.description = {} if desc is None else desc
        self.address = add
        self.gps_location = {} if gps is None else gps
        self.active = active
        self.created_at = arrow.utcnow().datetime
        self.updated_at = arrow.utcnow().datetime

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'logo': self.logo_img,
            'url': self.url,
            'description': self.description,
            'address': self.address,
            'gps_location': self.gps_location,
            'active': self.active
        }


class Report(Base):
    __tablename__ = 'reports'

    report_category_id = db.Column(db.Integer, db.ForeignKey('report_sub_categories.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    images = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=True)
    gps_location = db.Column(db.JSON)
    # 0: à espera, 1: em análise, 2: resolvido, 3: call (ligar para camara)
    state = db.Column(db.SmallInteger)
    is_remote = db.Column(db.Boolean)

    report_category = db.relationship('ReportSubCategory', backref='reports')

    def __init__(self, loc=None, rep_category=None, uid=None, images=0, desc=None, state=0, is_remote=False):
        self.report_category_id = rep_category
        self.user_id = uid
        self.gps_location = dict(
            lat=format(round(float(loc['lat']), 6), '.6f'),
            lng=format(round(float(loc['lng']), 6), '.6f'),
        )
        self.images = images
        self.description = desc
        self.state = state
        self.is_remote = is_remote
        self.created_at = arrow.utcnow().datetime
        self.updated_at = arrow.utcnow().datetime

    def to_json(self):
        return dict(
            id=self.id,
            submitted_at=str(self.created_at).split(".")[0],
            humanized_date=arrow.get(self.created_at).to('utc').humanize(locale='pt_PT'),
            user=dict(id=self.user.id, name=self.user.username, email=self.user.email),
            images=['report_imgs/' + str(self.id) + '/' + str(i) + ".jpg" for i in range(0, self.images)],
            description=self.description,
            state=self.state,
            gps_location=self.gps_location,
            category=self.report_category.to_json()
        )


class ReportCategory(Base):
    __tablename__ = 'report_categories'

    name = db.Column(db.JSON, nullable=False)

    def __init__(self, name=None):
        self.name = {} if name is None else name
        self.created_at = arrow.utcnow().datetime
        self.updated_at = arrow.utcnow().datetime

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'sub_categories': [sc.to_json() for sc in self.sub_categories]
        }

    def simple_json(self):
        return dict(id=self.id, name=self.name)


class ReportSubCategory(Base):
    __tablename__ = 'report_sub_categories'

    name = db.Column(db.JSON, nullable=False)
    parent_category_id = db.Column(db.Integer, db.ForeignKey('report_categories.id'))

    parent_category = db.relationship('ReportCategory', backref='sub_categories', lazy='dynamic', uselist=True)

    def __init__(self, pid, name=None):
        self.parent_category_id = pid
        self.name = {} if name is None else name
        self.created_at = arrow.utcnow().datetime
        self.updated_at = arrow.utcnow().datetime

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'parent_category': self.parent_category.first().simple_json()
        }


class ShopItem(Base):
    __tablename__ = 'shop_items'

    name = db.Column(db.JSON)
    images = db.Column(db.JSON, nullable=False)
    description = db.Column(db.JSON)
    link = db.Column(db.String(255))
    cost = db.Column(db.Integer, nullable=False)
    limit = db.Column(db.JSON, nullable=True)
    partner_id = db.Column(db.Integer, db.ForeignKey('partners.id'), nullable=True)
    active = db.Column(db.Boolean)

    partner = db.relationship('Partner', backref='items')

    def __init__(self, name=None, partner_id=None, description=None, cost=0, images=[], limit=None, link=None):
        self.name = {} if name is None else name
        self.images = images
        self.description = {} if description is None else description
        self.cost = cost
        self.partner_id = partner_id
        self.active = True
        self.limit = limit
        self.link = link
        self.created_at = arrow.utcnow().datetime
        self.updated_at = arrow.utcnow().datetime

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'images': self.images,
            'cost': self.cost,
            'description': self.description,
            'limit': self.limit,
            'partner': self.partner.to_json(),
            'active': self.active,
            'link': self.link
        }


temple_categories = db.Table('temples_categories',
                             db.Column('temples_id', db.Integer, db.ForeignKey('temples.id'), primary_key=True),
                             db.Column('temple_category_id', db.Integer, db.ForeignKey('temple_categories.id'),
                                       primary_key=True)
                             )


class Temple(Base):
    __tablename__ = 'temples'

    name = db.Column(db.JSON, nullable=False)
    geometry = db.Column(db.JSON)
    description = db.Column(db.JSON, nullable=True)
    active = db.Column(db.Boolean)
    tribe_points = db.Column(db.JSON)
    activity = db.Column(db.JSON)
    past_conquerors = db.Column(db.JSON)

    categories = db.relationship('TempleCategory', secondary=temple_categories, backref='temples',
                                 uselist=True, lazy='dynamic')

    def __init__(self, name=None, geometry=None, desc=None, types=None):
        self.name = dict(pt="", en="") if name is None else name
        self.geometry = self.filter_geometry(geometry)
        self.description = dict(pt="", en="") if desc is None else desc
        self.active = True
        self.tribe_points = dict(fire=0, water=0, earth=0, wind=0, spirit=0)
        self.categories = [
            TempleCategory.query.filter(cast(TempleCategory.name['en'], String) == type_coerce(t, JSON)).first() for t
            in types]
        self.past_conquerors = []
        self.activity = []
        self.created_at = arrow.utcnow().datetime
        self.updated_at = arrow.utcnow().datetime

    def get_activity_stats(self):
        stats2 = {'total': 0, 'earth': 0, 'water': 0, 'fire': 0, 'wind': 0, 'spirit': 0}
        res = {'visit': {'recent': [], 'stats': dict(stats2)},
               'collect': {'recent': [], 'stats': dict(stats2)},
               'tribute': {'recent': [], 'stats': dict(stats2)}}

        for entry in self.activity:
            res[entry['action']]['stats']['total'] += 1
            res[entry['action']]['stats'][entry['tribe']] += 1
            if len(res[entry['action']]['recent']) < 5:
                its_in = False
                for pos in res[entry['action']]['recent']:
                    if int(entry['id']) == int(pos['id']):
                        its_in = True
                        break
                if not its_in:
                    res[entry['action']]['recent'].append(entry)

        return res

    def update_activity(self, action, user):
        new_entry = {'id': user['id'],
                     'name': user['username'],
                     'tribe': user['tribe'],
                     'datetime': str(arrow.utcnow().datetime),
                     'action': action}
        self.activity.insert(0, dict(new_entry))

        flag_modified(self, 'activity')

    @staticmethod
    def filter_geometry(geometry):
        g = {
            'location': {'lat': None, 'lng': None},
            'viewport': {
                'nw': {'lat': None, 'lng': None},
                'se': {'lat': None, 'lng': None}
            }
        }
        if geometry is not None:
            if 'location' in geometry:
                loc = geometry['location']
                if 'lat' in loc and 'lng' in loc and loc['lat'] is not None and loc['lng'] is not None:
                    g['location'] = {
                        'lat': float(format(round(float(loc['lat']), 6), '.6f')),
                        'lng': float(format(round(float(loc['lng']), 6), '.6f')),
                    }
            if 'viewport' in geometry:
                vp = geometry['viewport']
                if 'west' in vp and 'east' in vp and 'north' in vp and 'south' in vp:
                    w, e, n, s = vp['west'], vp[
                        'east'], vp['north'], vp['south']
                    if w is not None and e is not None and n is not None and s is not None:
                        g['viewport'] = {
                            'nw': {'lat': float(format(round(float(n), 6), '.6f')),
                                   'lng': float(format(round(float(w), 6), '.6f'))},
                            'se': {'lat': float(format(round(float(s), 6), '.6f')),
                                   'lng': float(format(round(float(e), 6), '.6f'))}
                        }

        return g

    def current_conqueror(self):
        conqueror = max(self.tribe_points, key=self.tribe_points.get)
        return 'neutral' if self.tribe_points[conqueror] == 0 else conqueror

    def get_images(self):
        path = join(TEMPLE_IMG_FOLDER, str(self.id))
        return [join(path, f).replace("\\", "/") for f in listdir(path) if isfile(join(path, f))]

    def to_json(self):
        return {
            'id': self.id,
            'active': self.active,
            'images': self.get_images(),
            'name': self.name,
            'description': self.description,
            'location': self.geometry['location'],
            'categories': [tc.to_json() for tc in self.categories.all()],
            'tribe_point_count': self.tribe_points,
            'conqueror': self.current_conqueror(),
            'past_conquerors': self.past_conquerors,
            'activity_stats': self.get_activity_stats()
        }

    def light_json(self):
        return {
            'id': self.id,
            'location': self.geometry['location'],
            'conqueror': self.current_conqueror(),
            'tribe_point_count': self.tribe_points,
        }

    def to_print(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'categories': [tc.name['en'] for tc in self.categories.all()],
            'geometry': self.geometry
        }


class TempleCategory(Base):
    __tablename__ = 'temple_categories'

    name = db.Column(db.JSON, nullable=False)

    def __init__(self, name):
        self.name = name
        self.created_at = arrow.utcnow().datetime
        self.updated_at = arrow.utcnow().datetime

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name
        }


class Tribe(Base):
    __tablename__ = 'tribes'

    element = db.Column(db.JSON, nullable=False)
    motto = db.Column(db.JSON, nullable=False)
    description = db.Column(db.JSON)

    users = db.relationship('User', backref='tribe', lazy='dynamic')

    def __init__(self, element=None, description=None, motto=None):
        self.element = {} if element is None else element
        self.description = {} if description is None else description
        self.motto = {} if motto is None else motto

    def to_json(self):
        return {
            'id': self.id,
            'element': self.element,
            'motto': self.motto,
            'description': self.description
        }


class User(Base):
    __tablename__ = 'users'

    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(45), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=True)
    gender = db.Column(db.Integer, nullable=False)
    dob = db.Column(db.Date, nullable=True)
    is_admin = db.Column(db.Boolean)
    is_blocked = db.Column(db.Boolean)
    level = db.Column(db.Integer, nullable=False)
    actions = db.Column(db.JSON)
    progress = db.Column(db.JSON)
    inventory = db.Column(db.JSON)
    tribe_id = db.Column(db.Integer, db.ForeignKey('tribes.id'), nullable=True)
    city_zone_id = db.Column(db.Integer, db.ForeignKey('city_zones.id'), nullable=True)
    # activity_log = db.Column(db.JSON)

    reports_sent = db.relationship('Report', backref='user', lazy='dynamic')

    authenticated = False
    active = True
    anonymous = True

    def __init__(self, un, e, pw, dob=None, gender=0, admin=False, cz=-1, tribe_id=1, blocked=False):
        self.created_at = arrow.utcnow().datetime
        self.updated_at = arrow.utcnow().datetime
        self.username = un
        self.email = e
        self.password = pwd_context.encrypt(pw)
        self.is_admin = admin
        self.gender = gender
        self.dob = arrow.get(dob, 'YYYY-M-D').date()
        self.progress = dict(achievements=self.start_achievs(), dailies={}, events={})
        self.actions = dict(visit=dict(count=0), tribute=dict(count=0), collect=dict(count=0), exchange=dict(count=0))
        self.tribe_id = tribe_id
        self.city_zone_id = None if cz == -1 else cz
        self.level = 1
        self.is_blocked = blocked
        self.activity_log = []
        self.inventory = dict(points=dict(total=0, current=0),
                              essences=dict(fire=dict(total=0, current=0),
                                            water=dict(total=0, current=0),
                                            wind=dict(total=0, current=0),
                                            spirit=dict(total=0, current=0),
                                            earth=dict(total=0, current=0)
                                            ))

    def get_avatar(self):
        return '/static/user_ppics/' + str(self.id) + '/0.jpg'

    def get_id(self):
        return self.id

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return self.anonymous

    def verify_password(self, password):
        return pwd_context.verify(password, self.password)

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    def is_tourist(self):
        return self.city_zone_id is None

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = User.query.get(data['id'])
        return user

    @staticmethod
    def start_achievs():
        achieves = {}
        families = [a.family for a in Achievement.query.distinct(Achievement.family)]
        for f in families:
            achieves[f] = dict(current_chain_level=0)
            for a in Achievement.query.filter_by(family=f).all():
                achieves[f][str(a.id)] = dict(completed=False, collected=False)
        return achieves

    def discovered_temple(self, temple_id):
        return temple_id in self.actions['visit'] and len(self.actions['visit'][str(temple_id)]) > 0

    def execute_temple_action(self, temple, action, pos):
        me = Point(latitude=float(format(pos['lat'], '.6f')), longitude=float((format(pos['lng'], '.6f'))))
        temple_position = Point(latitude=float(temple.geometry['location']['lat']),
                                longitude=float(temple.geometry['location']['lng']))
        tid = str(temple.id)
        if tid not in self.actions[action]:
            self.actions[action][tid] = []

        if vincenty(me, temple_position).kilometers * 1000 <= 15:
            now = arrow.utcnow()
            if action == 'tribute':
                if self.check_and_consume_essences_for_tribute():
                    self.actions[action][tid].insert(0, str(now.datetime))
                    self.actions[action]['count'] += 1
                    temple.tribe_points[self.tribe.element['en']] += 1

                    level_changed = self.change_point_count(quantity=150)

                    '''
                    self.activity_log.insert(0, dict(action=action,
                                                     date=str(now.datetime),
                                                     temple=dict(id=int(temple.id), name=temple.name['pt'])
                                                     ))
                    '''
                    temple.update_activity(action=action, user=dict(id=self.id,
                                                                    username=self.username,
                                                                    tribe=self.tribe.element['en']))
                    self.progress = self.verify_achievement_progress(family=action)
                    return {
                        'inventory': self.inventory,
                        'progress': self.progress,
                        'actions': self.actions,
                        'level_changed': level_changed,
                        'to_next_level': self.to_next_level(),
                        'conqueror': temple.current_conqueror(),
                        'tribe_tributes': temple.tribe_points
                    }
                else:
                    return 0
            elif action == 'exchange':
                return 0
            elif action == 'collect':
                if len(self.actions[action][tid]) > 0:
                    last = arrow.get(self.actions[action][tid][0]).datetime
                    # if difference less than 3 minutes, not valid
                    if (now.datetime - last).seconds / 60 < 3:
                        return 0

                temple.update_activity(action=action, user=dict(id=self.id,
                                                                username=self.username,
                                                                tribe=self.tribe.element['en']))
                self.actions[action][tid].insert(0, str(now.datetime))
                self.actions[action]['count'] += 1
                self.activity_log.insert(0, dict(action=action,
                                                 date=str(now.datetime),
                                                 temple=dict(id=int(temple.id), name=temple.name['pt'])
                                                 ))
                flag_modified(self, 'activity_log')
                result = self.generate_essence_drop()
                level_changed = self.change_point_count(quantity=50)
                for elem, value in result.items():
                    self.change_essence_count(element=elem, quantity=value)

                self.progress = self.verify_achievement_progress(family=action)
                return {
                    'inventory': self.inventory,
                    'progress': self.progress,
                    'actions': self.actions,
                    'drop': result,
                    'level_changed': level_changed,
                    'to_next_level': self.to_next_level()
                }
            elif action == 'visit':

                temple.update_activity(action=action, user=dict(id=self.id,
                                                                username=self.username,
                                                                tribe=self.tribe.element['en']))

                self.activity_log.insert(0, dict(action=action,
                                                 date=str(now.datetime),
                                                 temple=dict(id=int(temple.id), name=temple.name['pt'])
                                                 ))
                if len(self.actions[action][tid]) > 0:
                    last = arrow.get(self.actions[action][tid][0]).datetime
                    # if difference less than 3 minutes, not valid
                    if (now.datetime - last).seconds / 60 < 1:
                        return {'temple_info': temple.to_json(), 'in_range': True}

                self.actions[action][str(tid)].insert(0, str(now.datetime))
                self.actions[action]['count'] += 1

                conq = temple.current_conqueror()
                if conq != 'neutral':
                    self.change_essence_count(element=conq, quantity=5)

                level_changed = self.change_point_count(quantity=10)

                self.progress = self.verify_achievement_progress(family=action)

                return {
                    'temple_info': temple.to_json(),
                    'inventory': self.inventory,
                    'progress': self.progress,
                    'actions': self.actions,
                    'level_changed': level_changed,
                    'to_next_level': self.to_next_level(),
                    'in_range': True
                }
            else:
                return 0
        if action == 'visit':
            return {'temple_info': temple.to_json(), 'in_range': False}
        return -1

    def verify_achievement_progress(self, family):
        import copy
        actions = ['collect', 'exchange', 'visit', 'tribute']
        progress = copy.deepcopy(self.progress)
        if family in actions:
            current = self.actions[family]['count']
            achievs = Achievement.query.filter_by(family=family).order_by(Achievement.chain_level).all()
            current_chain_level = progress['achievements'][family]['current_chain_level']
            for index in range(current_chain_level, len(achievs)):
                a = achievs[index]
                if current >= a.extra_info['quantity']:
                    if not self.progress['achievements'][family][str(a.id)]['completed']:
                        self.progress['achievements'][family][str(a.id)]['completed'] = True
                        self.progress['achievements'][family]['current_chain_level'] += 1
                else:
                    break

        elif family == 'level':
            pass
        return progress

    def change_point_count(self, quantity):
        before = self.to_next_level()
        self.inventory['points']['total'] += quantity
        self.inventory['points']['current'] += quantity
        if before['points_left'] <= quantity:
            self.level += 1

        return before['points_left'] <= quantity

    def change_essence_count(self, element, quantity):
        self.inventory['essences'][element]['total'] += quantity
        self.inventory['essences'][element]['current'] += quantity

    def generate_essence_drop(self):
        elements = ['fire', 'water', 'earth', 'wind', 'spirit']
        return {elem: randint(8, 15) if elem == self.tribe.element['en'] else randint(0, 7) for elem in elements}

    def check_and_consume_essences_for_tribute(self):
        my_tribe = self.tribe.element['en']
        for elem, count in self.inventory['essences'].items():
            if (elem == my_tribe and self.inventory['essences'][my_tribe]['current'] < 10) or (
                    elem != my_tribe and self.inventory['essences'][elem]['current'] < 5):
                return False

        for elem, count in self.inventory['essences'].items():
            self.inventory['essences'][elem]['current'] -= 10 if elem == my_tribe else 5

        return True

    def to_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'tribe': self.tribe.element['en'],
            'city_zone': self.city_zone.to_json(),
            'is_blocked': self.is_blocked,
            'is_admin': self.is_admin,
            'gender': self.gender,
            'dob': str(self.dob),
            'level': self.level,
            'actions': self.actions,
            'progress': self.progress,
            # 'discovered_spots': [spot.id for spot in Temple.query.all() if self.discovered_spot(spot.id)],
            # 'reports_sent': [report.to_json() for report in self.reports_sent],
            'avatar': 'static/user_images/' + str(self.id) + '/0.jpg',
            'to_next_level': self.to_next_level(),
            'inventory': self.inventory
        }

    def get_activity_log(self):
        log = []
        for action, value in self.actions.items():
            for key, info in value.items():
                if key != 'count':
                    for timestamp in info:
                        log.append(dict(action=action, date=arrow.get(timestamp).to('utc'),
                                        temple=dict(id=int(key), name=Temple.query.get(int(key)).name['pt'])))

        for rep in self.reports_sent:
            rep_loc = Point(latitude=float(format(float(rep.gps_location['lat']), '.6f')),
                            longitude=float(format(float(rep.gps_location['lng']), '.6f')))

            near_temples = []
            for t in Temple.query.all():
                temple_loc = Point(latitude=float(format(float(t.geometry['location']['lat']), '.6f')),
                                   longitude=float(format(float(t.geometry['location']['lng']), '.6f')))
                dist = vincenty(rep_loc, temple_loc).kilometers * 1000
                if dist <= 500:
                    near_temples.append(dict(temple=t.id, dist=dist))

            near_temples = sorted(near_temples, key=lambda x: x['dist'], reverse=False)
            log.append(dict(
                action='report',
                rep_id=rep.id,
                date=arrow.get(rep.created_at).to('utc'),
                remote=rep.is_remote,
                near=dict(
                    id=int(near_temples[0]['temple']),
                    name=Temple.query.get(int(near_temples[0]['temple'])).name['pt']) if len(near_temples) > 0 else None
            ))

        log = sorted(log, key=lambda x: x['date'], reverse=True)
        return log

    def get_friend_list_status(self):
        lst = dict(friends=[], pending_sent=[], pending_received=[])
        for req in self.friend_reqs_sent:
            info = req.invitee.to_chat_json()
            info['date'], info['req_id'] = arrow.get(req.updated_at if req.is_accepted else req.created_at).to(
                'utc').humanize(locale='pt_PT'), req.id
            lst['friends'].append(info) if req.is_accepted else lst['pending_sent'].append(info)
        for req in self.friend_reqs_received:
            info = req.inviter.to_chat_json()
            info['date'], info['req_id'] = arrow.get(req.updated_at if req.is_accepted else req.created_at).to(
                'utc').humanize(locale='pt_PT'), req.id
            lst['friends'].append(info) if req.is_accepted else lst['pending_received'].append(info)

        lst['friends'] = sorted(lst['friends'], key=lambda x: x['name'].lower(), reverse=False)
        lst['pending_sent'] = sorted(lst['pending_sent'], key=lambda x: x['name'].lower(), reverse=False)
        lst['pending_received'] = sorted(lst['pending_received'], key=lambda x: x['name'].lower(), reverse=False)
        return lst

    def get_internal_messages_information(self):
        messages = dict(sent=[], received=dict(unread=0, list=[]))
        for m in self.received_messages:
            if not m.is_read:
                messages['received']['unread'] += 1
            messages['received']['list'].insert(0, dict(
                id=m.id,
                content=m.content,
                sender=dict(
                    id=m.sender.id,
                    name=m.sender.username,
                    avatar=m.sender.get_avatar()
                ),
                date=arrow.get(m.created_at).to('utc').humanize(locale='pt_PT'),
                is_read=m.is_read
            ))

        for m in self.sent_messages:
            messages['sent'].insert(0, dict(
                id=m.id,
                content=m.content,
                receiver=dict(
                    id=m.receiver.id,
                    name=m.receiver.username,
                    avatar=m.receiver.get_avatar()
                ),
                date=arrow.get(m.created_at).to('utc').humanize(locale='pt_PT')
            ))
        return messages

    def is_friend_and_get_friends_in_common(self, user):
        if user.id != self.id:

            my_friends = [req.inviter.id for req in self.friend_reqs_received if req.is_accepted] + \
                         [req.invitee.id for req in self.friend_reqs_sent if req.is_accepted]
            his_friends = [req.inviter.id for req in user.friend_reqs_received if req.is_accepted] + \
                          [req.invitee.id for req in user.friend_reqs_sent if req.is_accepted]

            state = 0
            if user.id in my_friends:
                state = 3
            elif user.id in [req.inviter.id for req in self.friend_reqs_received if not req.is_accepted]:
                state = 1
            elif user.id in [req.invitee.id for req in self.friend_reqs_sent if not req.is_accepted]:
                state = 2

            return dict(friends_in_common=[User.query.get(uid).to_chat_json() for uid in
                                           list(set(my_friends).intersection(his_friends))],
                        state=state)
        else:
            return None

    def get_profile_stats(self):
        tcs = TempleCategory.query.all()
        temples = Temple.query.filter_by(active=True).all()
        tc_visits = {st.name['en']: 0 for st in tcs}
        found_temples = []
        for key, value in self.actions['visit'].items():
            if key != 'count':
                if len(value) > 0:
                    if int(key) not in found_temples:
                        found_temples.append(int(key))
                    spot = Temple.query.get(int(key))
                    for entry in value:
                        for t in spot.categories:
                            tc_visits[t.name['en']] += 1

        stv_final = [dict(name_pt=st.name['pt'],
                          name_en=st.name['en'],
                          count=tc_visits[st.name['en']],
                          icon="_".join(st.name['en'].split(" "))) for st in TempleCategory.query.all()]

        stv_final = sorted(stv_final, key=lambda x: x['name_pt'], reverse=False)

        reports_sent = dict(
            total=len(self.reports_sent.all()),
            waiting=len(self.reports_sent.filter_by(state=0).all()),
            analysis=len(self.reports_sent.filter_by(state=1).all()),
            solved=len(self.reports_sent.filter_by(state=2).all()),
            special=len(self.reports_sent.filter_by(state=3).all())
        )

        achievements = dict(collected=0, completed=0, total=len(Achievement.query.all()))
        for family, info in self.progress['achievements'].items():
            for field, status in info.items():
                if field != 'current_chain_level':
                    if status['completed']:
                        achievements['completed'] += 1
                    if status['collected']:
                        achievements['collected'] += 1

        activity_log = self.get_activity_log()
        aloglen = len(activity_log)

        actions = dict(visits=int(self.actions['visit']['count']),
                       tributes=int(self.actions['tribute']['count']),
                       collects=int(self.actions['collect']['count']),
                       exchanges=int(self.actions['exchange']['count']),
                       reports=len(self.reports_sent.all()),
                       total=aloglen
                       )

        # meters_traveled
        meters_traveled = dict(today=0, this_week=0, this_month=0, this_year=0, total=0)
        today = arrow.utcnow().date()
        this_year, this_week_number, this_week_day = today.isocalendar()
        if aloglen > 1:
            for i in range(1, aloglen):
                event0 = activity_log[i - 1]
                if event0['action'] == 'report':
                    rep0 = Report.query.get(event0['rep_id'])
                    prev = Point(latitude=float(format(float(rep0.gps_location['lat']), '.6f')),
                                 longitude=float(format(float(rep0.gps_location['lng']), '.6f')))
                else:
                    t0 = Temple.query.get(event0['temple']['id'])
                    prev = Point(latitude=float(format(float(t0.geometry['location']['lat']), '.6f')),
                                 longitude=float(format(float(t0.geometry['location']['lng']), '.6f')))

                prev_date = arrow.get(event0['date']).to('utc').date()
                pyear, pwn, pwd = prev_date.isocalendar()

                event = activity_log[i]
                if event['action'] == 'report':
                    rep = Report.query.get(int(event['rep_id']))
                    curr = Point(latitude=float(format(float(rep.gps_location['lat']), '.6f')),
                                 longitude=float(format(float(rep.gps_location['lng']), '.6f')))
                else:
                    t = Temple.query.get(int(event['temple']['id']))
                    curr = Point(latitude=float(format(float(t.geometry['location']['lat']), '.6f')),
                                 longitude=float(format(float(t.geometry['location']['lng']), '.6f')))

                curr_date = arrow.get(event['date']).to('utc').date()
                cyear, cwn, cwd = curr_date.isocalendar()
                if (event0['action'] == 'report' and event0['remote']) or (
                        event['action'] == 'report' and event['remote']):
                    dist = 0
                else:
                    dist = int(vincenty(prev, curr).kilometers * 1000)
                if pyear == cyear and pyear == this_year:
                    meters_traveled['this_year'] += dist
                    if prev_date.month == curr_date.month and prev_date.month == today.month:
                        meters_traveled['this_month'] += dist
                    if pwn == cwn and pwn == this_week_number:
                        meters_traveled['this_week'] += dist
                        if pwd == cwd and pwd == this_week_day:
                            meters_traveled['today'] += dist
                meters_traveled['total'] += dist

        return dict(actions=actions,
                    reports_sent=reports_sent,
                    achievements=achievements,
                    discovered_temples=dict(found=len(found_temples),
                                            total=len(temples)),
                    spot_type_visits=stv_final,
                    meters_traveled=meters_traveled,
                    activity_log=activity_log)

    def to_next_level(self):
        import math
        total_points_needed_to_next_level = 0
        total_points_needed_to_current_level = 0
        for i in range(2, self.level + 2):
            if i <= 7:
                total_points_needed_to_next_level += 150 * math.pow((i - 1), 2) + 1050 * (i - 1)
                if i <= self.level:
                    total_points_needed_to_current_level += 150 * math.pow((i - 1) - 1, 2) + 1050 * (i - 1)

            elif 8 <= i <= 11:
                total_points_needed_to_next_level += 200 * math.pow((i - 1), 2) + 1050 * (i - 1) - 2450
                if i <= self.level:
                    total_points_needed_to_current_level += 200 * math.pow((i - 1), 2) + 1050 * (i - 1) - 2450

            elif 12 <= i <= 22:
                total_points_needed_to_next_level += 50 * math.pow((i - 1), 2) + 1750 * (i - 1) + 9800
                if i <= self.level:
                    total_points_needed_to_current_level += 50 * math.pow((i - 1), 2) + 1750 * (i - 1) + 9800

            elif 23 <= i <= 30:
                total_points_needed_to_next_level += 250 * math.pow((i - 1), 2) - 1500 * (i - 1) - 22750
                if i <= self.level:
                    total_points_needed_to_current_level += 250 * math.pow((i - 1), 2) - 1500 * (i - 1) - 22750

            else:
                pass

        max_points_to_next_level = total_points_needed_to_next_level - total_points_needed_to_current_level
        points_needed_to_next_level = total_points_needed_to_next_level - self.inventory['points']['total']
        percentage = float(100.0 - (points_needed_to_next_level * 100.0 / max_points_to_next_level))

        return dict(total_to_next_level=int(max_points_to_next_level),
                    points_left=int(points_needed_to_next_level),
                    percentage=format(percentage, '.1f'))

    def to_chat_json(self):
        return dict(
            id=self.id,
            name=self.username,
            tribe=self.tribe.element['en'],
            avatar=join(USER_IMAGES_FOLDER, str(self.id) + '/0.jpg'),
            level=self.level
        )

    def get_ranking_points(self):
        actions = self.actions
        year, week_number, week_day = arrow.utcnow().date().isocalendar()
        points_this_week = 0
        for action, values in actions.items():
            for key, entries in values.items():
                if key != 'count':
                    for entry in entries:
                        ey, ewn, ewd = arrow.get(entry).date().isocalendar()
                        if year == ey and week_number == ewn:
                            if action == 'collect':
                                points_this_week += 50
                            elif action == 'tribute':
                                points_this_week += 150
                            elif action == 'visit':
                                points_this_week += 10

        return dict(total=int(self.inventory['points']['total']),
                    this_week=points_this_week)


class InternalMessage(Base):
    __tablename__ = 'internal_messages'

    content = db.Column(db.String(255))
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    is_read = db.Column(db.Boolean)

    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')

    def __init__(self, receiver_id, sender_id=None, content="", read=False):
        self.content = content
        self.receiver_id = receiver_id
        self.sender_id = sender_id
        self.is_read = read
        self.created_at = arrow.utcnow().datetime
        self.updated_at = arrow.utcnow().datetime

    def is_system_message(self):
        return self.sender_id is None


class FriendRequest(Base):
    __tablename__ = 'friend_requests'

    inviter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    invitee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_accepted = db.Column(db.Boolean)

    inviter = db.relationship('User', foreign_keys=[inviter_id], backref='friend_reqs_sent')
    invitee = db.relationship('User', foreign_keys=[invitee_id], backref='friend_reqs_received')

    def __init__(self, src, dest, accepted=False):
        self.inviter_id = src
        self.invitee_id = dest
        self.is_accepted = accepted
        self.created_at = arrow.utcnow().datetime
        self.updated_at = arrow.utcnow().datetime

    def to_json(self):
        return {
            'id': self.id,
            'sent_at': self.created_at,
            'changed_at': self.updated_at,
            'inviter': self.inviter.to_json(),
            'invitee': self.invitee.to_json()
        }


events_missions = db.Table('events_missions',
                           db.Column('mission_id', db.Integer, db.ForeignKey('missions.id'), primary_key=True),
                           db.Column('event_id', db.Integer, db.ForeignKey('events.id'), primary_key=True)
                           )


class Mission(Base):
    __tablename__ = 'missions'

    name = db.Column(db.JSON, nullable=False)
    description = db.Column(db.JSON, nullable=False)
    # event_id = db.Column(db.Integer, db.ForeignKey('events.id'),
    # nullable=True)  # if null -> daily mission
    reward = db.Column(db.JSON, nullable=False)
    # {'type': 'pointxp'/'item', 'data': {'xp': 1000, 'points': 1000, 'item': ShopItem/None}}

    is_daily = db.Column(db.Boolean)

    def __init__(self, name=None, description=None, reward=None, is_daily=False):
        self.name = {} if name is None else name
        self.is_daily = is_daily
        self.description = {} if description is None else description
        self.reward = {'points': 0, 'items': [], 'essences': {
            'fire': 0, 'water': 0, 'wind': 0, 'spirit': 0, 'earth': 0
        }} if reward is None else reward
        self.created_at = arrow.utcnow().datetime
        self.updated_at = arrow.utcnow().datetime


class Event(Base):
    __tablename__ = 'events'

    name = db.Column(db.JSON, nullable=False)
    image = db.Column(db.String(255), nullable=True)
    # event_images/event_id.jpg
    description = db.Column(db.JSON, nullable=False)
    starts_at = db.Column(db.DateTime)
    ends_at = db.Column(db.DateTime)
    location = db.Column(db.JSON)  # {'lat': ..., 'lng': ... }
    # {'type': 'pointxp'/'item', 'data': {'xp': 1000, 'points': 1000, 'item': ShopItem/None}}
    reward = db.Column(db.JSON, nullable=False)

    missions = db.relationship(
        'Mission', secondary=events_missions, backref='events', uselist=True, lazy='dynamic')

    def __init__(self, starts_at, ends_at, name=None, description=None, location=None, reward=None, img=None):
        self.name = {} if name is None else name
        self.description = {} if description is None else description
        self.starts_at = (arrow.get(starts_at).to('utc')).datetime
        self.ends_at = (arrow.get(ends_at).to('utc')).datetime
        self.image = img
        self.location = {"lat": 41.441371, "lng": -8.295022} if location is None else self.parse_loc(location)
        self.reward = {'points': 0, 'items': [], 'essences': {
            'fire': 0, 'water': 0, 'wind': 0, 'spirit': 0, 'earth': 0
        }} if reward is None else reward
        self.created_at = arrow.utcnow().datetime
        self.updated_at = arrow.utcnow().datetime

    def is_ongoing(self):
        return self.has_started() and not self.is_over()

    def has_started(self):
        return arrow.get(self.starts_at).to('utc').datetime < arrow.utcnow().datetime

    def is_over(self):
        return arrow.get(self.ends_at).to('utc').datetime < arrow.utcnow().datetime

    @staticmethod
    def parse_loc(location):
        return {
            'lat': format(round(float(location['lat']), 6), '.6f'),
            'lng': format(round(float(location['lng']), 6), '.6f')
        }

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'starts_at': self.starts_at,
            'ends_at': self.ends_at,
            'location': self.location,
            'missions': [m.to_json() for m in self.missions.all()]
        }


'''
INSERT AUX FUNCTIONS
'''


def insert_users_and_friend_requests():
    db.session.add(User(
        un="monty",
        e="monty@mail.com",
        pw="123123",
        gender=0,
        dob="1989-08-06",
        tribe_id=5,
        cz=39
    ))
    db.session.add(User(
        un="andr3smp",
        e="andr3smp@mail.com",
        pw="123123",
        gender=0,
        dob="1989-08-06",
        tribe_id=2,
        cz=2
    ))
    db.session.add(User(
        un="CapRickz",
        e="rickz@mail.com",
        pw="123123",
        gender=0,
        dob="1989-08-06",
        tribe_id=5,
        cz=12
    ))
    db.session.add(User(
        un="Gyplex",
        e="gyplex@mail.com",
        pw="123123",
        gender=0,
        dob="1989-08-06",
        tribe_id=1,
        cz=30
    ))
    db.session.add(User(
        un="Aeign",
        e="aeign@mail.com",
        pw="123123",
        gender=0,
        dob="1989-08-06",
        tribe_id=4,
        cz=13
    ))
    db.session.add(User(
        un="H4uZ",
        e="hauz@mail.com",
        pw="123123",
        gender=0,
        dob="1989-08-06",
        tribe_id=3,
        cz=36
    ))

    tribe_ids = [t.id for t in Tribe.query.all()]
    city_zone_ids = [cz.id for cz in CityZone.query.all()]

    '''
    for i in range(0, 20):
        un = "utilizador" + str(i + 1).zfill(3)
        db.session.add(User(
            un=un,
            e=un + "@mail.com",
            pw="123123",
            gender=randint(-1, 1),
            dob=str(randint(1980, 2004)) + "-" + str(randint(1, 12)).zfill(2) + "-" + str(
                randint(1, 26)).zfill(2),
            tribe_id=choice(tribe_ids),
            cz=choice(city_zone_ids)
        ))
        print un + " created"
    '''
    db.session.commit()

    for user in User.query.all():
        if not exists(join(USER_IMAGES_FOLDER, str(user.id))):
            makedirs(join(USER_IMAGES_FOLDER, str(user.id)))

        if user.gender == 1:
            image = Image.open(join(USER_IMAGES_FOLDER, 'female.png')).convert('RGB')
        else:
            image = Image.open(join(USER_IMAGES_FOLDER, 'male.png')).convert('RGB')

        image.save(join(USER_IMAGES_FOLDER, str(user.id) + "\\0.jpg"), optimize=True, quality=85,
                   format='JPEG')

    db.session.add(FriendRequest(src=1, dest=2, accepted=True))
    db.session.add(FriendRequest(src=1, dest=3, accepted=False))
    db.session.add(FriendRequest(src=1, dest=4, accepted=False))

    db.session.add(FriendRequest(src=2, dest=3, accepted=True))
    db.session.add(FriendRequest(src=2, dest=4, accepted=False))

    db.session.add(FriendRequest(src=3, dest=5, accepted=True))
    db.session.add(FriendRequest(src=3, dest=6, accepted=False))

    db.session.add(FriendRequest(src=5, dest=1, accepted=False))
    db.session.add(FriendRequest(src=5, dest=6, accepted=False))

    db.session.add(FriendRequest(src=6, dest=1, accepted=False))
    db.session.commit()


def insert_city_zones():
    db.session.add(CityZone(name=u'Aldão'))
    db.session.add(CityZone(name=u'Azurém'))
    db.session.add(CityZone(name=u'Barco'))
    db.session.add(CityZone(name=u'Brito'))
    db.session.add(CityZone(name=u'Caldelas'))
    db.session.add(CityZone(name=u'Candoso (São Martinho)'))
    db.session.add(CityZone(name=u'Costa'))
    db.session.add(CityZone(name=u'Creixomil'))
    db.session.add(CityZone(name=u'Fermentões'))
    db.session.add(CityZone(name=u'Gonça'))
    db.session.add(CityZone(name=u'Gondar'))
    db.session.add(CityZone(name=u'Guardizela'))
    db.session.add(CityZone(name=u'Infantas'))
    db.session.add(CityZone(name=u'Longos'))
    db.session.add(CityZone(name=u'Lordelo'))
    db.session.add(CityZone(name=u'Mesão Frio'))
    db.session.add(CityZone(name=u'Moreira de Cónegos'))
    db.session.add(CityZone(name=u'Nespereira'))
    db.session.add(CityZone(name=u'Pencelo'))
    db.session.add(CityZone(name=u'Pinheiro'))
    db.session.add(CityZone(name=u'Polvoreira'))
    db.session.add(CityZone(name=u'Ponte'))
    db.session.add(CityZone(name=u'Prazins (Santa Eufémia)'))
    db.session.add(CityZone(name=u'Ronfe'))
    db.session.add(CityZone(name=u'Sande (São Martinho)'))
    db.session.add(CityZone(name=u'São Torcato'))
    db.session.add(CityZone(name=u'Selho (São Cristóvão)'))
    db.session.add(CityZone(name=u'Selho (São Jorge)'))
    db.session.add(CityZone(name=u'Serzedelo'))
    db.session.add(CityZone(name=u'Silvares'))
    db.session.add(CityZone(name=u'Urgezes'))
    db.session.add(CityZone(name=u'União das Freguesias de Abação e Gémeos'))
    db.session.add(CityZone(name=u'União das Freguesias de Airão Santa Maria, Airão S. João e Vermil'))
    db.session.add(CityZone(name=u'União das Freguesias de Arosa e Castelões'))
    db.session.add(CityZone(name=u'União das Freguesias de Atães e Rendufe'))
    db.session.add(CityZone(name=u'União das Freguesias de Briteiros Santo Estêvão e Donim'))
    db.session.add(CityZone(name=u'União das Freguesias de Briteiros S. Salvador e Briteiros Sta Leocádia'))
    db.session.add(CityZone(name=u'União das Freguesias de Candoso Santiago e Mascotelos'))
    db.session.add(CityZone(name=u'União das Freguesias de Conde e Gandarela'))
    db.session.add(CityZone(name=u'União das Freguesias de Leitões, Oleiros e Figueiredo'))
    db.session.add(CityZone(name=u'União das Freguesias de Oliveira, São Paio e São Sebastião'))
    db.session.add(CityZone(name=u'União das Freguesias de Prazins Santo Tirso e Corvite'))
    db.session.add(CityZone(name=u'União das Freguesias de Sande São Lourenço e Balazar'))
    db.session.add(CityZone(name=u'União das Freguesias de Sande Vila Nova e Sande São Clemente'))
    db.session.add(CityZone(name=u'União das Freguesias de Selho S. Lourenço e Gominhães'))
    db.session.add(CityZone(name=u'União das Freguesias de Serzedo e Calvos'))
    db.session.add(CityZone(name=u'União das Freguesias de Souto Sta Maria, Souto S. Salvador e Gondomar'))
    db.session.add(CityZone(name=u'União das Freguesias de Tabuadelo e São Faustino'))

    db.session.commit()


def insert_tribes():
    db.session.add(Tribe(element={'en': 'fire', 'pt': 'fogo'},
                         description={'en': '',
                                      'pt': 'A tribo do fogo simboliza a energia e a paixão do povo da cidade. Aposta no turismo e no comércio local como o caminho a seguir para um futuro melhor. O seu principal objectivo é mostrar o valor da cidade e dos seus cidadãos aos seus e aos de fora.'},
                         motto={'en': 'Passion for what is ours', 'pt': 'Paixão pelo que é nosso'}))
    db.session.add(Tribe(element={'en': 'water', 'pt': u'água'},
                         description={'en': '',
                                      'pt': 'A tribo da água simboliza a capacidade de mudança, adaptação e evolução. Promove a ciência e aposta no avanço tecnológico da cidade.'},
                         motto={'en': 'The world is changing, change with it',
                                'pt': 'O mundo está a mudar, muda com ele'}))
    db.session.add(Tribe(element={'en': 'spirit', 'pt': u'espírito'},
                         description={'en': '',
                                      'pt': 'Promovendo a criatividade, espontaneidade e a inventividade, a tribo do espírito tem as artes e o desporto como o estandarte do brilho e alma da cidade.'},
                         motto={'en': 'Express yourself, find happiness', 'pt': 'Expressa-te, encontra a felicidade'}))
    db.session.add(Tribe(element={'en': 'wind', 'pt': 'vento'},
                         description={'en': '',
                                      'pt': 'A tribo do vento pede cidadãos que mantenham uma mente aberta e que tenham a sabedoria de perceber que a saúde e a educação devem ser as principais preocupações da cidade. Criar futuras gerações mais sábias, atentas e com melhores condições de vida.'},
                         motto={'en': 'Observ, learn and grow', 'pt': 'Observa, aprende e cresce'}))
    db.session.add(Tribe(element={'en': 'earth', 'pt': 'terra'},
                         description={'en': '',
                                      'pt': 'A tribo da terra acredita que o povo e a cidade devem muito à história da mesma e à dureza e força das pessoas que ajudaram a construí-la. Vê o abraçar e aceitar a herança cultural e histórica da cidade, aprendendo com os erros e sucessos dos seus antecessores como o caminho certo para um futuro melhor da cidade.'},
                         motto={'en': 'Our heritage, our strengh', 'pt': 'A nossa herança, a nossa força'}))


def insert_temple_categories():
    db.session.add(TempleCategory(name=dict(en="school", pt="escola")))
    db.session.add(TempleCategory(name=dict(en="education", pt="educação")))
    db.session.add(TempleCategory(name=dict(en="historical", pt="histórico")))
    db.session.add(TempleCategory(name=dict(en="tourism", pt="turismo")))
    db.session.add(TempleCategory(name=dict(en="library", pt="biblioteca")))
    db.session.add(TempleCategory(name=dict(en="fire station", pt="bombeiros")))
    db.session.add(TempleCategory(name=dict(en="museum", pt="museu")))
    db.session.add(TempleCategory(name=dict(en="religion", pt="religião")))
    db.session.add(TempleCategory(name=dict(en="local government office", pt="governo local")))
    db.session.add(TempleCategory(name=dict(en="cemetery", pt="cemitério")))
    db.session.add(TempleCategory(name=dict(en="sports", pt="desportos")))
    db.session.add(TempleCategory(name=dict(en="park", pt="parque")))
    db.session.add(TempleCategory(name=dict(en="statue", pt="estátua")))
    db.session.add(TempleCategory(name=dict(en="train station", pt="estação de comboio")))
    db.session.add(TempleCategory(name=dict(en="entertainment", pt="entretenimento")))
    db.session.add(TempleCategory(name=dict(en="events", pt="eventos")))
    db.session.add(TempleCategory(name=dict(en="leisure", pt="lazer")))
    db.session.add(TempleCategory(name=dict(en="courthouse", pt="tribunal")))
    db.session.add(TempleCategory(name=dict(en="university", pt="universidade")))

    db.session.commit()


def insert_initial_temples():
    from spotsdatafile import spot_data

    count = 1
    for spot in spot_data:
        db.session.add(Temple(name=spot['name'],
                              geometry=spot['geometry'],
                              desc=None if spot['description'] == {} else spot['description'],
                              types=spot['types']
                              ))
        count += 1

    db.session.commit()


def insert_report_categories():
    db.session.add(ReportCategory(name=dict(pt=u"Animais", en="Animals")))
    db.session.add(ReportCategory(name=dict(pt=u"Sinalização de Trânsito", en="Traffic Signs")))
    db.session.add(ReportCategory(name=dict(pt=u"Semáforos", en="Traffic Lights")))
    db.session.add(ReportCategory(name=dict(pt=u"Placa de Rua", en="Street Sign")))
    db.session.add(ReportCategory(name=dict(pt=u"Segurança Rodoviária", en="Road Safety")))
    db.session.add(ReportCategory(name=dict(pt=u"Equipamentos Urbanos Danificados", en="Damaged Urban Equipment")))
    db.session.add(ReportCategory(name=dict(pt=u"Limpeza de Via Pública", en="Public Space Cleanliness")))
    db.session.add(ReportCategory(name=dict(pt=u"Danos no Espaço Público", en="Public Property Damage")))
    db.session.add(ReportCategory(name=dict(pt=u"Limpeza linhas de água", en="Water Lines Cleanliness")))

    db.session.commit()


def insert_report_sub_categories():
    db.session.add(
        ReportSubCategory(name=dict(pt=u"Vespas Velutinas/ Ninhos", en="Asian Predatory Wasp / Nests"), pid=1))
    db.session.add(ReportSubCategory(name=dict(pt=u"Cadáveres", en="Corpses"), pid=1))
    db.session.add(ReportSubCategory(name=dict(pt=u"Outros", en="Others"), pid=1))

    db.session.add(ReportSubCategory(name=dict(pt=u"Desaparecimento de Sinal", en="Sign Missing"), pid=2))
    db.session.add(ReportSubCategory(name=dict(pt=u"Sinal Derrubado", en="Sign Knocked Off"), pid=2))
    db.session.add(ReportSubCategory(name=dict(pt=u"Sinal Vandalizado", en="Vandalized Sign"), pid=2))

    db.session.add(ReportSubCategory(name=dict(pt=u"Desligados", en="Turned Off"), pid=3))
    db.session.add(ReportSubCategory(name=dict(pt=u"Mau Funcionamento", en="Malfunction"), pid=3))
    db.session.add(ReportSubCategory(name=dict(pt=u"Óticas Inoperacionais", en="Inoperative Optics"), pid=3))
    db.session.add(ReportSubCategory(name=dict(pt=u"Derrube", en="Knocked Over"), pid=3))

    db.session.add(ReportSubCategory(name=dict(pt=u"Vandalizada", en="Vandalized"), pid=4))
    db.session.add(ReportSubCategory(name=dict(pt=u"Derrubada", en="Knocked Over"), pid=4))
    db.session.add(ReportSubCategory(name=dict(pt=u"Inexistente", en="Non Existent"), pid=4))

    db.session.add(ReportSubCategory(name=dict(pt=u"Railes Danificados", en="Damaged Rail"), pid=5))
    db.session.add(ReportSubCategory(name=dict(pt=u"Outros", en="Others"), pid=5))

    db.session.add(ReportSubCategory(name=dict(pt=u"Abrigo de Passageiros", en="Bus Passengers\" Shelter"), pid=6))
    db.session.add(ReportSubCategory(name=dict(pt=u"Bancos de Jardim", en="Garden Benches"), pid=6))
    db.session.add(ReportSubCategory(name=dict(pt=u"Vedação de Madeira", en="Wood Fence"), pid=6))
    db.session.add(ReportSubCategory(name=dict(pt=u"Papeleiras", en="Paper Waste"), pid=6))
    db.session.add(ReportSubCategory(name=dict(pt=u"Parque Infantil", en="Playground"), pid=6))
    db.session.add(ReportSubCategory(
        name=dict(pt=u"Ecoponto, Contentor ou Molok", en="Recycling Spot, Garbage Container or Molok"),
        pid=6))

    db.session.add(ReportSubCategory(name=dict(pt=u"Lixo à Volta dos Contentores/Ecopontos",
                                               en="Trash around Recycling Spots or Garbage Containers"), pid=7))
    db.session.add(ReportSubCategory(
        name=dict(pt=u"Deposição de Lixo Fora de Horas", en="Garbage Disposal outside Permited Hours"),
        pid=7))
    db.session.add(ReportSubCategory(name=dict(pt=u"Contentores Cheios", en="Full Garbage Containers"), pid=7))
    db.session.add(ReportSubCategory(name=dict(pt=u"Varredura de Via Pública", en="Public Way Sweeping"), pid=7))
    db.session.add(ReportSubCategory(name=dict(pt=u"Lavagem de Passeios", en="Sidewalk Cleaning"), pid=7))
    db.session.add(
        ReportSubCategory(name=dict(pt=u"Recolha de Monstros na Via Pública", en="Bulky Garbage Collection"), pid=7))

    db.session.add(
        ReportSubCategory(name=dict(pt=u"Talude ou Muro em Risco", en="Slope or Wall in the Verge of Falling"),
                          pid=8))
    db.session.add(
        ReportSubCategory(name=dict(pt=u"Estrada ou Passeio Danificado", en="Damaged Road or Sidewalk"), pid=8))
    db.session.add(ReportSubCategory(name=dict(pt=u"Rotura Conduta", en="Broken Conduct"), pid=8))
    db.session.add(ReportSubCategory(name=dict(pt=u"Tampas de Saneamento", en="Manhole Covers"), pid=8))
    db.session.add(ReportSubCategory(name=dict(pt=u"Tampas Águas Pluviais", en="Drain Covers"), pid=8))
    db.session.add(ReportSubCategory(name=dict(pt=u"Candeeiros Danificados", en="Damaged Lamp Posts"), pid=8))
    db.session.add(ReportSubCategory(name=dict(pt=u"Outros", en="Others"), pid=8))

    db.session.add(ReportSubCategory(name=dict(pt=u"Lixo nas Margens Ribeirinhas", en="Riverside Waste"), pid=9))
    db.session.add(ReportSubCategory(name=dict(pt=u"Foco de Poluição", en="Pollution Spot"), pid=9))
    db.session.add(ReportSubCategory(name=dict(pt=u"Descarga", en="Flush"), pid=9))

    db.session.commit()


def insert_initial_fake_partners():
    # name, logo, add, gps={}, url=None, desc=None
    db.session.add(Partner(
        name=u'Vitória Sport Clube',
        logo=dict(type='url',
                  src='http://www.vitoriasc.pt/public/images/timeline/50131437062335.jpg'),
        add=u'Av. São Gonçalo, 4810 Guimarães',
        gps=dict(lat='41.445943', lng='-8.300960'),
        url='http://www.vitoriasc.pt/pt/',
        desc=dict(
            pt=u'O Vitória Sport Clube, também conhecido como Vitória ou pelo acrónimo VSC, é um clube desportivo fundado em 1922 e sediado na cidade de Guimarães, Portugal.')
    ))

    db.session.add(Partner(
        name=u'Lidl Vizela',
        logo=dict(type='url',
                  src='https://upload.wikimedia.org/wikipedia/en/thumb/b/be/Lidl_Stiftung_%26_Co._KG_logo.svg/1024px-Lidl_Stiftung_%26_Co._KG_logo.svg.png'),
        add='',
        url='https://www.lidl.pt/pt/index.htm',
        gps=dict(lat=None, lng=None)
    ))

    db.session.commit()


def insert_fake_shop_items():
    db.session.add(ShopItem(
        name={'pt': u'Bilhete Duplo VSC', 'en': 'Two Person Ticket VSC'},
        description={
            'pt': u'Bilhete duplo para jogo, em casa, do Vitória Sport Club, para desfrutar com um amigo, '
                  u'familiar ou parceiro, em jogo a determinar pelo clube.',
            'en': u'Two person ticket for Vitória Sport Club home game. Enjoy it with a friend or loved one. The '
                  u'club determines the game.'
        },
        partner_id=1,
        cost=5500,
        images=["bilhete.png"],
        limit={'quantity': 1, 'duration': 'month'}
    ))

    db.session.add(ShopItem(
        name={'pt': 'Equipamento principal VSC', 'en': 'VSC\'s Home Kit'},
        description={
            'pt': u'Equipamento principal do Vitória Sport Club da época 2017/18, disponível nos tamanhos S, M, L e XL',
            'en': u'Vitórias Sport Club 2017/18 season\'s home kit, available in Small, Medium, Large and Extra Large'
        },
        partner_id=1,
        cost=2250,
        images=["camisola.png", "dsc00012.jpg", "dsc00052.jpg", "dsc09971_1.jpg"],
        limit=None,
        link='http://webstore.vitoriasc.pt/equipamentos/principal/camisola-oficial-principal-17-18.html'
    ))

    db.session.commit()


def insert_dummy_events():
    '''
    db.session.add(Mission(
        name={'pt': 'Tributos à cidade', 'en': 'City tributes'},
        description={'pt': 'Fazer 10 tributos em templos da cidade',
                     'en': 'Make 10 tributes in any of the city\'s temples'},
        reward=None
    ))

    db.session.add(Mission(
        name={'pt': 'Homenagens, muitas homenagens', 'en': 'Much Honor, Such Wow'},
        description={'pt': 'Prestar 40 homenagens em templos da cidade',
                     'en': 'Honor 40 city temples'},
        reward=None
    ))

    db.session.commit()

    db.session.add(Event(starts_at='2017-11-30T11:35:59Z',
                         ends_at='2017-12-17T11:35:59Z',
                         name={'pt': 'Evento de teste 1', 'en': 'Test Event 1'},
                         description={'pt': 'grande descrição', 'en': 'big description'},
                         location={'lat': 41.4413713, 'lng': -8.295021900000002},
                         reward={'points': 150, 'items': [], 'essences': {
                             'fire': 30, 'water': 30, 'wind': 30, 'spirit': 30, 'earth': 30
                         }},
                         img=None))

    db.session.add(Event(starts_at='2017-10-27T11:35:59Z',
                         ends_at='2017-11-30T11:35:59Z',
                         name={'pt': 'Evento de teste 2', 'en': 'Test Event 2'},
                         description={'pt': 'grande descrição 2', 'en': 'big description 2'},
                         location={'lat': 41.4442573, 'lng': -8.292838800000027},
                         reward={'points': 0, 'items': [{'item_id': 2, 'quantity': 1}], 'essences': {
                             'fire': 100, 'water': 100, 'wind': 100, 'spirit': 100, 'earth': 100
                         }},
                         img=None))

    db.session.add(Event(starts_at='2017-10-10T11:35:59Z',
                         ends_at='2017-10-12T11:35:59Z',
                         name={'pt': 'Evento de teste 3', 'en': 'Test Event 3'},
                         description={'pt': 'grande descrição 3', 'en': 'big description 3'},
                         location={'lat': 41.4478935, 'lng': -8.2903191},
                         reward={'points': 500, 'items': [{'item_id': 1, 'quantity': 1}], 'essences': {
                             'fire': 250, 'water': 250, 'wind': 250, 'spirit': 250, 'earth': 250
                         }},
                         img=None))

    db.session.commit()

    Event.query.get(1).missions.append(Mission.query.get(1))
    Event.query.get(1).missions.append(Mission.query.get(2))
    Event.query.get(2).missions.append(Mission.query.get(1))
    Event.query.get(2).missions.append(Mission.query.get(2))
    Event.query.get(3).missions.append(Mission.query.get(1))
    Event.query.get(3).missions.append(Mission.query.get(2))
    db.session.commit()
    '''
    pass


def insert_achievements():
    vtc_values = [1, 10, 25, 50, 100, 250, 500, 1000]

    for i in range(0, len(vtc_values)):
        db.session.add(Achievement(
            name={"pt": "Turista nível " + str(i + 1)},
            desc={"pt": "Visitar " + str(vtc_values[i]) + " templos da cidade",
                  "en": "Visit " + str(vtc_values[i]) + " city temples"},
            reward={
                'points': 0,
                'items': [],
                'essences': {
                    'fire': 30 * (i + 1),
                    'water': 30 * (i + 1),
                    'wind': 30 * (i + 1),
                    'spirit': 30 * (i + 1),
                    'earth': 30 * (i + 1)
                }
            },
            chain_level=i,
            family='visit',
            extra={'quantity': vtc_values[i]}
        ))
        db.session.add(Achievement(
            name={"pt": "Contributo para a tribo " + str(i + 1)},
            desc={"pt": "Fazer " + str(vtc_values[i]) + " tributos em templos da cidade",
                  "en": "Make " + str(vtc_values[i]) + " tributes at city temples"},
            reward={
                'points': 150,
                'items': [],
                'essences': {
                    'fire': 300 * (i + 1),
                    'water': 300 * (i + 1),
                    'wind': 300 * (i + 1),
                    'spirit': 300 * (i + 1),
                    'earth': 300 * (i + 1)
                }
            },
            chain_level=i,
            family='tribute',
            extra={'quantity': vtc_values[i]}
        ))
        db.session.add(Achievement(
            name={"pt": "Colecionador nível " + str(i + 1)},
            desc={"pt": "Coletar essências " + str(vtc_values[i]) + " vezes em templos da cidade",
                  "en": "Essence collection " + str(vtc_values[i]) + " times at city temples"},
            reward={
                'points': 150,
                'items': [],
                'essences': {
                    'fire': 150 * (i + 1),
                    'water': 150 * (i + 1),
                    'wind': 150 * (i + 1),
                    'spirit': 150 * (i + 1),
                    'earth': 150 * (i + 1)
                }
            },
            chain_level=i,
            family='collect',
            extra={'quantity': vtc_values[i]}
        ))

    levels = [5, 10, 15, 20, 25, 30]
    for i in range(0, len(levels)):
        db.session.add(Achievement(
            name={"pt": "Nómada nível " + str(i + 1)},
            desc={"pt": "Chegar ao nível " + str(levels[i]),
                  "en": "Reach level " + str(levels[i])},
            reward={
                'points': 500 * (i + 1),
                'items': [],
                'essences': {
                    'fire': 0,
                    'water': 0,
                    'wind': 0,
                    'spirit': 0,
                    'earth': 0
                }
            },
            chain_level=i,
            family='level',
            extra={'level': levels[i]}
        ))

    db.session.commit()


def insert_fake_reports():
    db.session.add(Report(loc={"lat": "41.404586", "lng": "-8.325276"},
                          uid=1,
                          images=3,
                          desc="Alguém deixou sofás todos estragados perto da rua da igreja",
                          rep_category=27))
    db.session.commit()


def main():
    if len(CityZone.query.all()) == 0:
        insert_city_zones()
        print('------ City Zones inserted ------')

    if len(Tribe.query.all()) == 0:
        insert_tribes()
        print('------ Tribes inserted ------')

    if len(Achievement.query.all()) == 0:
        insert_achievements()
        print('------ Achievements inserted ------')

    if len(TempleCategory.query.all()) == 0:
        insert_temple_categories()
        print('------ Temple categories inserted ------')

    if len(ReportCategory.query.all()) == 0:
        insert_report_categories()
        print('------ Report Categories inserted ------')
        insert_report_sub_categories()
        print('------ Report Sub-Categories inserted ------')

    if len(Partner.query.all()) == 0:
        insert_initial_fake_partners()
        print('------ Fake Partners inserted ------')

    if len(Temple.query.all()) == 0:
        insert_initial_temples()
        print('------ Temples inserted ------')

    if len(ShopItem.query.all()) == 0:
        insert_fake_shop_items()
        print('------ Shot Items inserted ------')

    if len(User.query.all()) == 0 or len(FriendRequest.query.all()) == 0:
        insert_users_and_friend_requests()
        print('------ Users and Friend Requests inserted ------')

    if len(Report.query.all()) == 0:
        insert_fake_reports()
        print('------ Fake Reports inserted ------')
