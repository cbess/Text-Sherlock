# -*- coding: utf-8 -*-
# refs: http://flask.pocoo.org/docs/quickstart/#redirects-and-errors

import os
from server import app
from flask import render_template, request, abort
from core.sherlock import indexer, searcher, transformer
from core import settings as core_settings
from core.utils import debug, read_file


def results_from_search_text(text, pagenum=1, isPath=False, type=None):
    """Returns the results from the search using the given text, populated with the transformed items
    """
    idx = indexer.get_indexer().get_index()
    # find something in the index
    if isPath:
        results = idx.search_path(text)
    else:
        try:
            results = idx.search(text, pagenum, core_settings.RESULTS_PER_PAGE)
        except ValueError, e:
            # This assumes the value error resulted from an page count issue
            app.logger.error('Out of page bounds: %s' % e)
            return []
    # transform the results
    trns = transformer.Transformer()
    return trns.transform_results(results, type)
    

@app.route('/')
def index():
    """Handles index requests
    """
    response = {
        "title" : u"Welcome"
    }
    return render_template('index.html', **response)
    

@app.route('/search', methods=['POST', 'GET'])
def search():
    """Handles search requests
    """
    # get form vars
    if request.method == 'POST':
        form = request.form
    else:
        form = request.args
    search_text = form.get('q')
    pagenum = int(form.get('p', 1))
    app.logger.debug('page %d, searching for: %s' % (pagenum, search_text))
    results = results_from_search_text(search_text, pagenum)
    # build response
    response = {
        'title' : 'Search',
        'search_text' : search_text,
        'results' : results.items,
        'total_count' : results.total_count,
        'page' : {
            'current' : pagenum,
            'previous' : results.prev_pagenum,
            'next' : results.next_pagenum,
            'count' : len(results)
        }
    }
    return render_template('index.html', **response)


@app.route('/document', methods=['GET'])
def document():
    """Handles document display requests
    """
    root_dir = core_settings.INDEX_PATH % { 'sherlock_dir' : core_settings.ROOT_DIR }
    full_path = request.args.get('path')
    # if the full path wasn't appended, then append it (assumes path exist in default index path)
    if root_dir not in full_path:
        full_path = os.path.join(root_dir, full_path)
    search_text = request.args.get('q')
    pagenum = request.args.get('p')
    # perform the text search, get wrapped results
    results = results_from_search_text(full_path, isPath=True)
    if not results:
        app.logger.error('Unable to find document: %s' % full_path)
        abort(404)
    doc = results.items[0]
    doc_contents = read_file(full_path)
    # get syntax highlighted html
    trn = transformer.Transformer()
    doc_html = trn.to_html(doc_contents, doc.result.filename)
    # build response
    response = {
        "title" : doc.result.filename,
        'doc' : doc,
        'contents' : doc_html,
        'search_text' : search_text,
        'page_number' : pagenum
    }
    return render_template('document.html', **response)