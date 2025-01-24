from . import models
 

def RequestObjectMiddleware(get_response):

    def middleware(request):

        models.request_object = request
        resposnse = get_response(request)

        return resposnse

    return middleware