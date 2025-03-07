from radio.models import Suggest
from tools.table import to_dt
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect

@csrf_protect
def submit_suggestions(request):
    artists = request.GET.getlist('artists[]')
    track = request.GET.get('track')
    track_id = request.GET.get('track_id')
    sub_date= to_dt()

    artists = str([artist for artist in artists]).strip("[]\"'") # comma seperated artists
    
    # add to db
    new = Suggest(artists=artists, sub_date=sub_date, track=track, track_id=track_id)
    new.save()

    return HttpResponse(f'{track_id}: {artists}, {track}')
