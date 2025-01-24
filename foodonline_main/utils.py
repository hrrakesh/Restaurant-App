def get_or_set_current_location(request):
    
    lat = lng = None

    if 'lat' in request.session and 'lng' in request.session: # when user does not provide the lat and lng in the url
        lat = request.session['lat']
        lng = request.session['lng']

    elif 'lat' in request.GET: # getting from url
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')
        request.session['lat'] = lat
        request.session['lng'] = lng
    return lng, lat