#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class UserLogin(Resource):
    
    # login method
    def post(self):
        data = request.get_json()
        user = User.query.filter(User.username == data['username']).first()
        session['user_id'] = user.id
        response = make_response(
            user.to_dict(),
            200
        )
        return response
    

class ClearSession(Resource):

    # logout
    def delete(self):
    
        session['page_views'] = None
        session['user_id'] = None

        return {'message': 'No Content'}, 204
    

class CheckSession(Resource):

    def get(self):
        user = User.query.filter(User.id == session.get('user_id')).first()

        if user:
            return user.to_dict()
        else:
            # return {'message': '401: Not Authorized'}, 401
            return {}, 401

class IndexArticle(Resource):
    
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200

class ShowArticle(Resource):

    def get(self, id):
        session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
        session['page_views'] += 1

        if session['page_views'] <= 3:

            article = Article.query.filter(Article.id == id).first()
            article_json = jsonify(article.to_dict())

            return make_response(article_json, 200)

        return {'message': 'Maximum pageview limit reached'}, 401

api.add_resource(ClearSession, '/logout')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')
api.add_resource(UserLogin, '/login')
api.add_resource(CheckSession, '/check_session')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
