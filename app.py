# main.py
from flask import Flask, render_template, request
from urllib.parse import unquote
import requests
import re

regex = r'(?<=btih:)(?P<hash>[^&]*).*&dn=(?P<name>[^&]*)'
regex_btdig = r'(?<=<title>)(?P<name>[^\s]*)(?= torrent)'
base_url = 'https://btdig.com/search?q='

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        magnet = request.form.get('magnet')
        filepath = request.form.get('filepath')
        
        magnet = str(magnet)
        valid_input = re.match(r'magnet:\?xt=urn:[a-z0-9]+:[a-zA-Z0-9]{32}', magnet)
        if not valid_input:
            return render_template('index.html', error_message='Invalid input. Please enter a valid magnet link.')

        matches = re.search(regex, magnet, re.MULTILINE)

        # if no dn in magnet link fall back to scraping btdig
        if not matches.group('name'):
            print('falling back to btdig')
            page = requests.get(base_url+magnet)
            matches = re.search(regex_btdig, page.text, re.MULTILINE)

        # if no name in btdig fall back to using hash as name
        if not matches.group('name'):
            render_template('index.html', error_message='Could not get torrent name. Using hash.')
            torrent_name = matches.group('hash')

        # make torrent name human readable
        torrent_name = unquote(matches.group('name'))

        filepath = 'symlinks/' + filepath + torrent_name + '.magnet'
        with open(filepath, 'w') as file:
            file.write(magnet)

        return render_template('index.html', ok_message=f'Successfully sent {torrent_name} to blackhole!')

    return render_template('index.html')
 
if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5000)
    app.run(debug=True)
