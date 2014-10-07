
from django.conf import settings
from django.utils import simplejson

from django.template import Context, loader

from django.core.context_processors import csrf

from django.http import HttpResponse, HttpResponseBadRequest
import uuid
import os
def Upload(request):
    options = {
           "maxfilesize": 2 * 2 ** 20, 
           "minfilesize": 1 * 2 ** 10, # 1 Kb
           "acceptedformats": (
                               "image/jpeg","image/png",
                               )
           }
    if request.method == 'POST':
        temp_path = os.path.join(settings.PROJECT_ROOT, "tmp")
        if not ("f" in request.GET.keys()):
            if not request.FILES:
                if not request.POST[u"uid"]:
                    return HttpResponseBadRequest("UID not specified.")
                uid = request.POST[u"uid"]
                temp_path = os.path.join(temp_path, uid)
                file = request.FILES[u'files[]']
                error = False
                if file.size > options["maxfilesize"]:
                    error = "maxFileSize"
                    if file.size < options["minfilesize"]:
                        error = "minFileSize"
                        if file.content_type not in options["acceptedformats"]:
                            error = "acceptFileTypes"
                            response_data = {
                                             "name": file.name,
                                             "size": file.size,
                                             "type": file.content_type
                                             }
                            if error:
                                response_data["error"] = error
                                response_data = simplejson.dumps([response_data])
                                return HttpResponse(response_data, mimetype='application/json')
                            if not os.path.exists(temp_path):
                                os.makedirs(temp_path)
                                filename = os.path.join(temp_path, str(uuid.uuid4()) + file.name)
                                destination = open(filename, "wb+")
                                for chunk in file.chunks():
                                    destination.write(chunk)
                                    destination.close()
                                    import urllib
                                    response_data["delete_url"] = request.path + "?" + urllib.urlencode({"f": uid + "/" + os.path.split(filename)[1]})
                                    response_data["delete_type"] = "POST"
                                    response_data = simplejson.dumps([response_data])
                                    response_type = "application/json"
                                    if "text/html" in request.META["HTTP_ACCEPT"]:
                                        response_type = "text/html"
                                        return HttpResponse(response_data, mimetype=response_type)
        else:
                                        filepath = os.path.join(temp_path, request.GET["f"])
                                        if not os.path.isfile(filepath):
                                            return HttpResponseBadRequest("File does not exist")
                                        os.remove(filepath)
                                        response_data = simplejson.dumps(True)
                                        return HttpResponse(response_data, mimetype="application/json")
    else: 
        t = loader.get_template("upload.html")
        c = Context({
                     "uid": uuid.uuid4(),
                                                     "open_tv": u'{{',
                                                     "close_tv": u'}}',
                                                     "maxfilesize": options["maxfilesize"],
                                                     "minfilesize": options["minfilesize"],
                                                     })
        c.update(csrf(request))
        return HttpResponse(t.render(c))
