import json

import requests

from MKVTag import tagtools
from MKVTag.scrapers import _tools


__author__ = 'Odd'


poster_thumbnails_path = "http://image.tmdb.org/t/p/w185"
poster_path = 'http://image.tmdb.org/t/p/original'
backdrop_small_path = 'http://image.tmdb.org/t/p/w780'
backdrop_path = 'http://image.tmdb.org/t/p/original/'


#TODO make a translation tool (mkvtag = moviedbtag), difflib isn't as cool as expected
api_key = _tools.get_apikey('themoviedb')

def search(movie_name):
    """movie_name (string) -> list(dict())"""
    request = requests.get(
        'http://api.themoviedb.org/3/search/movie?api_key=' + api_key + '&query=' + movie_name)
    searchjson = json.loads(request.text)
    if "status_code" in searchjson and searchjson['status_code'] == 6:
        raise Exception("Wrong search: " + movie_name)
    movie_result = list()
    for result in searchjson['results']:
        movie_result.append({'title': result['title'],
                             'release': "" if result['release_date'] is "" else result['release_date'][0:result['release_date'].index('-')],
                             'thumbnail': poster_thumbnails_path + result['poster_path']
                             if result['poster_path'] is not None else "",
                             'id': result['id']})
    return movie_result


def get_info(id):
    request = requests.get(
        'http://api.themoviedb.org/3/movie/' + str(id) + '?api_key=' + api_key + '&append_to_response=credits')
    searchjson = json.loads(request.text)
    if "status_code" in searchjson and searchjson['status_code'] == 6:
        raise Exception("Wrong search: " + id)
    collection_info = dict()
    if 'belongs_to_collection' in searchjson and searchjson['belongs_to_collection'] is not None:
        for tag in searchjson['belongs_to_collection']:
            try:
                collection_info[tagtools.find_tagname(tag)] = searchjson['belongs_to_collection'][tag]
            except Exception:
                pass
        del searchjson['belongs_to_collection']

    genres = list()
    for genre in searchjson['genres']:
        genres.append(genre['name'])
    searchjson['genres'] = genres
    production_comp = list()
    for company in searchjson['production_companies']:
        production_comp.append(company['name'])
    del searchjson['production_companies']
    del searchjson['production_countries']
    searchjson['production_studio'] = production_comp
    item_info = dict()
    for crewmember in searchjson['credits']['crew']:
        if crewmember['job'] in ['Set Decoration', 'Sculptor']:
            pass
        elif crewmember['job'] in searchjson:
            searchjson[crewmember['job']].append(crewmember['name'])
        else:
            searchjson[crewmember['job']] = [crewmember['name']]
    actors = list()
    for actor in searchjson['credits']['cast']:
        actors.append([actor['name'], actor['character']])
    searchjson['actor'] = actors
    del searchjson['credits']
    for tag in searchjson:
        try:
            item_info[tagtools.find_tagname(tag)] = searchjson[tag]
        except Exception:
            pass
    appendages = dict()
    appendages['cover_small.jpg'] = "" if searchjson['poster_path'] is None else \
        poster_thumbnails_path + searchjson['poster_path']
    appendages['cover_land.jpg'] = "" if searchjson['backdrop_path'] is None else \
        backdrop_path + searchjson['backdrop_path']
    appendages['cover.jpg'] = "" if searchjson['poster_path'] is None else \
        poster_path + searchjson['poster_path']
    appendages['cover_land_small.jpg'] = "" if searchjson['backdrop_path'] is None else \
        backdrop_small_path + searchjson['backdrop_path']
    return {'collection': collection_info, 'item': item_info, 'attachments': appendages}

if __name__ == '__main__':
    #print(search("Captain America"))
    print(get_info('100402'))
    #print(get_info('13995'))