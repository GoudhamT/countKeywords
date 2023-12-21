import os
from flask import Flask, render_template, request, abort
from cfenv import AppEnv
from sap import xssec

class WordCounter:
    def __init__(self, uaa_service):
        self.uaa_service = uaa_service
        self.words_count = {}

    def authorize_request(self, access_token):
        security_context = xssec.create_security_context(access_token, self.uaa_service)
        return security_context.check_scope('uaa.resource')

    def count_words(self, keywords, content):
        self.words_count = {}
        words = set(keywords.split(',')) if len(keywords) > 1 else set()
        
        if words:
            for word in words:
                word = word.lower()
                self.words_count[word] = self.words_count.get(word, 0) + content.lower().count(word)

app = Flask(__name__)
port = int(os.environ.get('PORT', 3000))
env = AppEnv()
uaa_service = env.get_service(name='PDFScannergetCount-oauth').credentials

word_counter = WordCounter(uaa_service)

@app.route('/')
def UI():
    return render_template("index.html")

@app.route('/wordsCount', methods=('POST',))
def admin():
    if 'authorization' not in request.headers:
        abort(403)

    access_token = request.headers.get('authorization')[7:]
    is_authorized = word_counter.authorize_request(access_token)

    if not is_authorized:
        abort(403)

    keywords = request.form.get('keywords')
    extract_content = request.form.get('content')

    word_counter.count_words(keywords, extract_content)
    
    return word_counter.words_count

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
