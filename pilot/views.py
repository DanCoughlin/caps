# Create your views here.
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile 
from django.db import transaction
import os.path 
import string
from services import identity, fixity


def default(request):
    return render_to_response('index.html')

def getIdentifier(request):
    id = identity.mint()

    if (identity.validate(id) ):
        return render_to_response('identifier.html', {'identifier' : id });
    else:
        return render_to_response('identifier.html', {'identifier' : "0" });        

def getFixity(request):
    fil = "/dlt/users/dmc186/dltmap.js"
    algorithm = 'md5'
    h = fixity.generate(fil, algorithm)
    return render_to_response('fixity.html', {'fixity' : h, 'filename': fil, 'algorithm': algorithm});
