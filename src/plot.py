from datetime import date, datetime, timedelta
try:
    from .song_history import load_df
    from .song_history import  get_durations
except:
    from song_history import load_df
    from song_history import  get_durations
import pandas as pd 
import plotly.offline as opy
pd.options.plotting.backend = "plotly"

def to_html(figure):
    context = {}
    div = opy.plot(figure, auto_open=False, output_type='div')
    context['plot'] = div
    return context

def artist_duration(n=37):
    df, mdf = load_df()
    df = select_month(df, 7)

    durations = get_durations(list(set(df.id)))
    df = df.merge(durations, on='id', how='left')

    df_artist_track = df.groupby(['artist', 'id'])
    duration = df_artist_track['duration'].sum()
    count = df_artist_track.count()['played_at'] 

    total_time_artist = (count*duration).groupby('artist').sum()
    total_time_artist.sort_values(ascending=True, inplace=True)

    top_artists_ms = total_time_artist.tail(n)

    top_artists = top_artists_ms//(1000*60)  # minutes:1000*60   hours:1000*60*60

    top_artists = pd.DataFrame(top_artists).reset_index()
    top_artists.columns=['artist', 'time']
    top_artists.rename(columns={"time":"minutes"}, inplace=True)
    top_artists.index = [f'Rank: {n-i}' for i in range(n)]

    figure = top_artists.plot.barh(
        x = 'minutes',
        y = 'artist',
        color='minutes',
        hover_name = top_artists.index,
        template='plotly_dark'
    )
    figure.update(layout_showlegend=False)

    return to_html(figure)

def song_plays(n=37):
    print('Downloading to df()...')
    df, mdf = load_df()
    df = select_month(df, 7)

    name_artist = df.groupby(['name', 'artist', 'id'])  # TODO: maybe ids in front?
    _counts = name_artist.size().reset_index(name='play_count')
    sorted_counts = _counts.sort_values('play_count', ascending=True)
    top_songs = sorted_counts.tail(n)

    # ############# this should all be inside a duration f #############
    durations = get_durations(top_songs.id.unique())
    df = top_songs.merge(durations, how='left', on='id')

    df["minutes"] = (df.play_count * df.duration)/(1000*60)  # mintues:1000*60   hours:1000*60*60
    df.sort_values("minutes", ascending=True, inplace=True)

    df.index = ['Rank: '+str(n-i) for i in range(n)]

    df.rename(columns={"play_count":"count"}, inplace=True)

    #############HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH###################

    figure = df.plot.barh(
        y = 'name',
        x = 'minutes',
        labels = {
            'artist':'Artist',
            'name': 'Track',
        },
        custom_data = ['artist', 'name'],
        color='count',
        hover_name = df.index,
        hover_data=['artist', 'name', 'count'],
        template='plotly_dark'
    )
    figure.update_layout(
        showlegend=False
    )
    return to_html(figure)

def select_month(df, months=6):
    n_months_ago = (date.today() - timedelta(days=months*30)).strftime("%Y-%m-%dT00:00:00.000Z")
    return df[df.played_at > n_months_ago]


#### other tools #####

def show_named_plotly_colours():
    """
    function to display to user the colours to match plotly's named
    css colours.

    Reference:
        #https://community.plotly.com/t/plotly-colours-list/11730/3

    Returns:
        plotly dataframe with cell colour to match named colour name

    """
    s='''
        aliceblue, antiquewhite, aqua, aquamarine, azure,
        beige, bisque, black, blanchedalmond, blue,
        blueviolet, brown, burlywood, cadetblue,
        chartreuse, chocolate, coral, cornflowerblue,
        cornsilk, crimson, cyan, darkblue, darkcyan,
        darkgoldenrod, darkgray, darkgrey, darkgreen,
        darkkhaki, darkmagenta, darkolivegreen, darkorange,
        darkorchid, darkred, darksalmon, darkseagreen,
        darkslateblue, darkslategray, darkslategrey,
        darkturquoise, darkviolet, deeppink, deepskyblue,
        dimgray, dimgrey, dodgerblue, firebrick,
        floralwhite, forestgreen, fuchsia, gainsboro,
        ghostwhite, gold, goldenrod, gray, grey, green,
        greenyellow, honeydew, hotpink, indianred, indigo,
        ivory, khaki, lavender, lavenderblush, lawngreen,
        lemonchiffon, lightblue, lightcoral, lightcyan,
        lightgoldenrodyellow, lightgray, lightgrey,
        lightgreen, lightpink, lightsalmon, lightseagreen,
        lightskyblue, lightslategray, lightslategrey,
        lightsteelblue, lightyellow, lime, limegreen,
        linen, magenta, maroon, mediumaquamarine,
        mediumblue, mediumorchid, mediumpurple,
        mediumseagreen, mediumslateblue, mediumspringgreen,
        mediumturquoise, mediumvioletred, midnightblue,
        mintcream, mistyrose, moccasin, navajowhite, navy,
        oldlace, olive, olivedrab, orange, orangered,
        orchid, palegoldenrod, palegreen, paleturquoise,
        palevioletred, papayawhip, peachpuff, peru, pink,
        plum, powderblue, purple, red, rosybrown,
        royalblue, saddlebrown, salmon, sandybrown,
        seagreen, seashell, sienna, silver, skyblue,
        slateblue, slategray, slategrey, snow, springgreen,
        steelblue, tan, teal, thistle, tomato, turquoise,
        violet, wheat, white, whitesmoke, yellow,
        yellowgreen
        '''
    li=s.split(',')
    li=[l.replace('\n','') for l in li]
    li=[l.replace(' ','') for l in li]

    import pandas as pd
    import plotly.graph_objects as go

    df=pd.DataFrame.from_dict({'colour': li})
    fig = go.Figure(data=[go.Table(
      header=dict(
        values=["Plotly Named CSS colours"],
        line_color='black', fill_color='white',
        align='center', font=dict(color='black', size=14)
      ),
      cells=dict(
        values=[df.colour],
        line_color=[df.colour], fill_color=[df.colour],
        align='center', font=dict(color='black', size=11)
      ))
    ])

    fig.show()

######################


'''
Checklist of things to do:
    X hours per artist
    X songs plays with color 
    - genre plots?
'''

if __name__=='__main__':
    # print('Downloading to df()...')
    # df, mdf = load_df()

    artist_duration()
    song_plays()

    print('end')




