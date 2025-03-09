try:
    from authorize import get_token
except:
    from.authorize import get_token
import requests as r
from django.shortcuts import render


def search(query_str='', types='track'):  # only search for tracks for now
    token = get_token()
    URL = "https://api.spotify.com/v1/search"   
    HEAD = {'Authorization': 'Bearer '+token} 
    PARAMS = {'q': query_str, 'type':types}
    response = r.get(url=URL, headers=HEAD, params=PARAMS).json()
    
    results = []
    for t in types.split(','):
        items = response[t+'s']['items']
        for item in items:
            artists = [a['name'] for a in item['artists']]
            results.append({'artists': artists, 
                            'track':item['name'],
                            'artwork':item['album']['images'][0]['url'],
                            'url':item['external_urls']['spotify'],
                            'id': item['id']})
            
    return results

def Http_search(request):
    query_str = request.GET.get('query_str')
    results = search(query_str=query_str)
    return render(None, 'includes/search.html', {'results': results})
