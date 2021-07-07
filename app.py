from flask import Flask,jsonify,request,Response
from flask_cors import CORS
from flask_restplus import Api, Resource, fields
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from skill_extractor import get_skills
from cv_extractor import LanguageModel,Parsing
import os
lm = LanguageModel('data_for_extract.txt')

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.0', 
    title='Work-Seeker Provider',
    default='v1',
    default_label='')
CORS(app)

app.config['UPLOAD_FOLDER']="uploads"
ALLOWED_EXTENSIONS = {'pdf','docx','txt','doc'}
os.makedirs(app.config['UPLOAD_FOLDER'],exist_ok = True)
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

parser = api.parser()
parser.add_argument('text', location='form',type=str)
parser.add_argument('file', location='files',type=FileStorage)

@api.route('/skill_extractor')
class main_class(Resource):
	@api.expect(parser)
	def post(self):
		text=request.form.get('text')
		print(text,not text)
		if not text and 'file' in request.files:
		    file = request.files['file']
		    filename = secure_filename(file.filename)
		    if not allowed_file(file.filename):
		    	return "Please select pdf or doc file",400
		    file_path=os.path.join(app.config['UPLOAD_FOLDER'], filename)
		    file.save(file_path)
		    p = Parsing(file_path,lm)
		    text=p.results
		# else:
		# 	return "Please select file or input text",400
		result=get_skills(text,True)
		return result
if __name__ == '__main__':
	app.run(host='0.0.0.0',port=8080,debug=True)