from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from flask_cors import CORS
from datetime import datetime
import openpyxl

# Initialize Flask app
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
api = Api(app)

# Models
class Website(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    domain = db.Column(db.String(100), unique=True, nullable=False)

class Keyword(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(100), nullable=False, unique=True)
    websites = db.relationship('Website', secondary='keyword_website', backref='keywords', lazy='dynamic')

keyword_website = db.Table('keyword_website',
    db.Column('keyword_id', db.Integer, db.ForeignKey('keyword.id'), primary_key=True),
    db.Column('website_id', db.Integer, db.ForeignKey('website.id'), primary_key=True)
)

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    keyword_id = db.Column(db.Integer, db.ForeignKey('keyword.id'), nullable=False)
    website_id = db.Column(db.Integer, db.ForeignKey('website.id'), nullable=False)
    min_rank = db.Column(db.Integer, nullable=False)
    max_rank = db.Column(db.Integer, nullable=False)
    avg_rank = db.Column(db.Float, nullable=False)  # Store avg_rank as a float for precision
    suggestions = db.Column(db.JSON, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    keyword = db.relationship('Keyword', backref=db.backref('results', lazy=True))
    website = db.relationship('Website', backref=db.backref('results', lazy=True))

    def __init__(self, keyword_id, website_id, min_rank, max_rank, avg_rank, suggestions=None):
        self.keyword_id = keyword_id
        self.website_id = website_id
        self.min_rank = min_rank
        self.max_rank = max_rank
        self.avg_rank = avg_rank
        self.suggestions = suggestions

    @staticmethod
    def calculate_avg_rank(min_rank, max_rank, number_of_review):
        if number_of_review > 0:
            return (min_rank + max_rank) / number_of_review
        return 0.0

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(15), nullable=False)
    http_method = db.Column(db.String(10), nullable=False)
    path = db.Column(db.String(200), nullable=False)
    status_code = db.Column(db.Integer, nullable=False)

# Helper function to log actions
def log_action(action, details=None):
    # Get the request details
    ip_address = request.remote_addr
    http_method = request.method
    path = request.path
    status_code = 200  # Default status code for now

    log_entry = Log(
        action=action,
        details=details,
        ip_address=ip_address,
        http_method=http_method,
        path=path,
        status_code=status_code
    )
    db.session.add(log_entry)
    db.session.commit()

# Logging every request before it is processed
@app.before_request
def log_request():
    # Only log requests to GET /keywords and POST /results
    if request.method == 'GET' and request.path == '/bot':
        log_action('GET /bot', details=f"{request.method} {'/keywords'}")

    elif request.method == 'POST' and request.path == '/bot':
        log_action('POST /bot', details=f"{request.method} {'/results'}")

# API Resources
class WebsiteResource(Resource):
    def get(self):
        websites = Website.query.all()
        return jsonify([{'id': w.id, 'name': w.name, 'domain': w.domain} for w in websites])

    def post(self):
        data = request.json
        if not data.get('name') or not data.get('domain'):
            return jsonify({'message': 'Name and domain are required'}), 400

        if Website.query.filter_by(domain=data['domain']).first():
            return jsonify({'message': 'Website with this domain already exists'}), 400

        new_website = Website(name=data['name'], domain=data['domain'])
        try:
            db.session.add(new_website)
            db.session.commit()
            log_action('Add Website', f"Website '{data['domain']}' added.")
            return jsonify({'message': 'Website added successfully', 'website': {'id': new_website.id, 'name': new_website.name, 'domain': new_website.domain}})
        except Exception as e:
            db.session.rollback()
            log_action('Add Website Error', str(e))
            return jsonify({'error': str(e)}), 500

    def delete(self):
        data = request.json
        if not data.get('id'):
            return jsonify({'message': 'ID is required'}), 400

        website = Website.query.get(data['id'])
        if website:
            try:
                # Delete the website and its associations
                for keyword in website.keywords:
                    website.keywords.remove(keyword)

                db.session.delete(website)
                db.session.commit()
                log_action('Delete Website', f"Website '{website.domain}' deleted.")
                return jsonify({'message': 'Website deleted successfully'})
            except Exception as e:
                db.session.rollback()
                log_action('Delete Website Error', str(e))
                return jsonify({'error': str(e)}), 500

        return jsonify({'message': 'Website not found'}), 404

    def put(self):
        data = request.json
        if not data.get('id') or not data.get('name') or not data.get('domain'):
            return jsonify({'message': 'ID, name, and domain are required'}), 400

        website = Website.query.get(data['id'])
        if website:
            if Website.query.filter(Website.domain == data['domain'], Website.id != data['id']).first():
                return jsonify({'message': 'Another website with this domain already exists'}), 400

            website.name = data['name']
            website.domain = data['domain']
            try:
                db.session.commit()
                log_action('Update Website', f"Website '{website.domain}' updated.")
                return jsonify({'message': 'Website updated successfully'})
            except Exception as e:
                db.session.rollback()
                log_action('Update Website Error', str(e))
                return jsonify({'error': str(e)}), 500

        return jsonify({'message': 'Website not found'}), 404


class KeywordResource(Resource):
    def get(self):
        keywords = Keyword.query.all()
        return jsonify([{'id': k.id, 'keyword': k.keyword, 'websites': [{'id': w.id, 'name': w.name, 'domain': w.domain} for w in k.websites]} for k in keywords])

    def post(self):
        data = request.json
        if not data.get('keyword') or not data.get('website_ids'):
            return jsonify({'message': 'Keyword and associated website IDs are required'}), 400

        if Keyword.query.filter_by(keyword=data['keyword']).first():
            return jsonify({'message': 'Keyword already exists'}), 400

        new_keyword = Keyword(keyword=data['keyword'])
        for site_id in data['website_ids']:
            site = Website.query.get(site_id)
            if site:
                new_keyword.websites.append(site)
        try:
            db.session.add(new_keyword)
            db.session.commit()
            log_action('Add Keyword', f"Keyword '{data['keyword']}' added.")
            return jsonify({'message': 'Keyword added successfully', 'keyword': {'id': new_keyword.id, 'keyword': new_keyword.keyword}})
        except Exception as e:
            db.session.rollback()
            log_action('Add Keyword Error', str(e))
            return jsonify({'error': str(e)}), 500

    def delete(self):
        data = request.json
        if not data.get('id'):
            return jsonify({'message': 'ID is required'}), 400

        keyword = Keyword.query.get(data['id'])
        if keyword:
            try:
                # Remove associations from the keyword_website table
                for website in keyword.websites:
                    keyword.websites.remove(website)

                # Delete the keyword itself
                db.session.delete(keyword)
                db.session.commit()

                log_action('Delete Keyword', f"Keyword '{keyword.keyword}' deleted.")
                return jsonify({'message': 'Keyword deleted successfully'})
            except Exception as e:
                db.session.rollback()
                log_action('Delete Keyword Error', str(e))
                return jsonify({'error': str(e)}), 500

        return jsonify({'message': 'Keyword not found'}), 404

    def put(self):
        data = request.json
        if not data.get('id') or not data.get('keyword') or not data.get('website_ids'):
            return jsonify({'message': 'ID, keyword, and associated website IDs are required'}), 400

        keyword = Keyword.query.get(data['id'])
        if keyword:
            if Keyword.query.filter(Keyword.keyword == data['keyword'], Keyword.id != data['id']).first():
                return jsonify({'message': 'Another keyword with this text already exists'}), 400

            keyword.keyword = data['keyword']
            keyword.websites = []  # Clear current associations

            for site_id in data['website_ids']:
                site = Website.query.get(site_id)
                if site and site not in keyword.websites:
                    keyword.websites.append(site)

            try:
                db.session.commit()
                log_action('Update Keyword', f"Keyword '{keyword.keyword}' updated.")
                return jsonify({'message': 'Keyword updated successfully'})
            except Exception as e:
                db.session.rollback()
                log_action('Update Keyword Error', str(e))
                return jsonify({'error': str(e)}), 500

        return jsonify({'message': 'Keyword not found'}), 404


class ExcelUploadResource(Resource):
    def post(self):
        if 'file' not in request.files:
            return jsonify({'message': 'No file part'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'message': 'No selected file'}), 400

        if file and file.filename.endswith('.xlsx'):
            try:
                wb = openpyxl.load_workbook(file)
                sheet = wb.active

                for row in sheet.iter_rows(min_row=2, values_only=True):
                    keyword_text = row[0]
                    website_domains = row[1].split(',')

                    keyword = Keyword.query.filter_by(keyword=keyword_text).first()
                    if not keyword:
                        keyword = Keyword(keyword=keyword_text)

                    for domain in website_domains:
                        website = Website.query.filter_by(domain=domain.strip()).first()
                        if website and website not in keyword.websites:
                            keyword.websites.append(website)

                    db.session.add(keyword)
                    db.session.flush()  # Incrementally commit changes to avoid memory overflow

                db.session.commit()
                log_action('Upload Excel', 'Keywords and websites uploaded successfully.')
                return jsonify({'message': 'File uploaded and data processed successfully'})
            except Exception as e:
                db.session.rollback()
                log_action('Excel Upload Error', str(e))
                return jsonify({'error': str(e)}), 500

        return jsonify({'message': 'Invalid file format. Only .xlsx files are supported.'}), 400

class LogsResource(Resource):
    def get(self):
        logs = Log.query.order_by(Log.timestamp.desc()).all()
        return jsonify([
            {
                'id': log.id,
                'action': log.action,
                'details': log.details,
                'timestamp': log.timestamp,
                'ip_address': log.ip_address,
                'http_method': log.http_method,
                'path': log.path,
                'status_code': log.status_code
            }
            for log in logs
        ])
class ResultsResource(Resource):
    def post(self):
        data = request.json

        # Validate incoming data
        if not data or 'keyword' not in data or 'domain' not in data or 'min_rank' not in data or 'max_rank' not in data or 'avg_rank' not in data or 'suggestions' not in data:
            return {'message': 'Keyword, domain, min_rank, max_rank, avg_rank, and suggestions are required'}, 400

        keyword_text = data['keyword']
        domain = data['domain']
        min_rank = data['min_rank']
        max_rank = data['max_rank']
        avg_rank = data['avg_rank']
        suggestions = data['suggestions']

        # Find the keyword in the database
        keyword = Keyword.query.filter_by(keyword=keyword_text).first()
        if not keyword:
            return {'message': 'Keyword not found'}, 404

        # Find the website in the database
        website = Website.query.filter_by(domain=domain).first()
        if not website:
            return {'message': 'Website not found'}, 404

        try:
            # Save results in the "Result" model
            result = Result(
                keyword_id=keyword.id,
                website_id=website.id,
                min_rank=min_rank,
                max_rank=max_rank,
                avg_rank=avg_rank,
                suggestions=suggestions
            )
            db.session.add(result)
            db.session.commit()

            return {'message': 'Search results processed successfully and saved to the database'}, 200

        except Exception as e:
            db.session.rollback()
            log_action('Search Results Error', str(e))
            return {'error': str(e)}, 500

    def get(self):
        # Optional: retrieve results based on a specific keyword or date range
        keyword_param = request.args.get('keyword', None)
        start_date = request.args.get('start_date', None)
        end_date = request.args.get('end_date', None)

        query = Result.query

        if keyword_param:
            keyword = Keyword.query.filter_by(keyword=keyword_param).first()
            if not keyword:
                return {'message': 'Keyword not found'}, 404
            query = query.filter_by(keyword_id=keyword.id)

        if start_date:
            query = query.filter(Result.timestamp >= datetime.fromisoformat(start_date))

        if end_date:
            query = query.filter(Result.timestamp <= datetime.fromisoformat(end_date))

        results = query.all()

        # Prepare data for response
        response_data = []
        for result in results:
            response_data.append({
                'keyword': result.keyword.keyword,
                'website': {
                    'id': result.website.id,
                    'name': result.website.name,
                    'domain': result.website.domain,
                },
                'min_rank': result.min_rank,
                'max_rank': result.max_rank,
                'avg_rank': result.avg_rank,
                'suggestions': result.suggestions,
                'timestamp': result.timestamp.isoformat()  # Return timestamp in ISO format
            })

        return {'results': response_data}, 200

class botResource(Resource):
    def get(self):
        # Optional: retrieve results based on a specific keyword or date range
        return {'message': 'bot Get'}
    def post(self):
        return {'message': 'bot Post'}

# Add the ResultsResource to the API
api.add_resource(ResultsResource, '/results')

api.add_resource(WebsiteResource, '/websites')
api.add_resource(KeywordResource, '/keywords')
#api.add_resource(ExcelUploadResource, '/upload_excel')
api.add_resource(botResource, '/bot')
api.add_resource(LogsResource, '/logs')

@app.route('/')
def home():
    return "API is running!"
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
