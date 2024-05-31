# main.py
from flask import Flask, render_template, request
from urllib.parse import unquote
import requests
import re

regex = r'urn:btih:(?P<hash>[a-fA-F0-9]{40})(?:&.*dn=(?P<name>[^&]+))?'
regex_btdig = r'(?<=<title>)(?P<name>[^\s]*)(?= torrent)'
base_url = 'https://btdig.com/search?q='

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        magnets = request.form.get('magnet')
        folder = request.form.get('filepath')
        
        magnet_links = magnets.splitlines()
        
        error_messages = []
        success_messages = []

        for magnet in magnet_links:
            magnet = str(magnet)
            valid_input = re.match(r'magnet:\?xt=urn:[a-z0-9]+:[a-zA-Z0-9]{32}', magnet)

            if not valid_input:
                error_messages.append(f'Invalid input: {magnet}')
                continue
            
            matches = re.search(regex, magnet)

            # if no dn in magnet link fall back to scraping btdig
            if not matches.group('name'):
                print('falling back to btdig')
                page = requests.get(base_url + magnet)
                matches = re.search(regex_btdig, page.text)

            # if no name in btdig fall back to using hash as name
            if not matches.group('name'):
                torrent_name = matches.group('hash')
                error_messages.append(f'Could not get torrent name for magnet: {magnet}. Using hash: {torrent_name}.')
            else:
                # make torrent name human readable only if it isnt the hash
                torrent_name = unquote(matches.group('name'))

            filepath = 'symlinks/' + folder + torrent_name + '.magnet'
            with open(filepath, 'w') as file:
                file.write(magnet)

            success_messages.append(f'Successfully sent {torrent_name} to blackhole!')

        return render_template('index.html', success_messages=success_messages, error_messages=error_messages)

    return render_template('index.html')
 
if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5000)
    app.run(debug=True)
