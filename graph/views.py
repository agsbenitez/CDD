from django.shortcuts import render
from django.http import HttpResponse
import matplotlib.pyplot as plt
import numpy as np

import math as mt
import mpld3

import base64
from io import BytesIO


# Create your views here.

def graph_seno(request):
    context = dict()

    if(request.GET):
        form_data = request.GET.dict()
        if not form_data.get('frq') or form_data.get('frq') == 0:
            context['frq'] = 1
        else:
            context['frq'] = int(form_data.get('frq'))

        if not form_data.get('amp') or form_data.get('amp') == 0:
            context['amp'] = 1
        else:
            context['amp'] = int(form_data.get('amp'))
    else:
        context['frq'] = 1
        context['amp'] = 1

    def seno(x):
        return mt.sin(x)
    

    def move_spines():
        fix, ax = plt.subplots()
        for spine in ["left", "bottom"]:
            ax.spines[spine].set_position("zero")

        for spine in ["right", "top"]:
            ax.spines[spine].set_color("none")

        return ax


    fig = plt.figure()

    ax = move_spines()
    ax = fig.subplots()
    ax.spines["left"].set_position("zero")
    ax.spines["bottom"].set_position("zero")
    ax.spines["right"].set_color("none")
    ax.spines["top"].set_color("none")

    ax.grid()

    var = np.arange(0, 11, 0.1)
   
    #plt.plot(var,[seno(i) for i in var], label= 'Seno')
    #plt.xlim(-10, 10)
    #plt.ylim(-10, 10)
    #plt.legend(loc='lower right')
    ax.plot(var,[context['amp'] *seno(i * context['frq']) for i in var], label= 'Seno')
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    image_png = buf.getvalue()
    # Embed the result in the html output.
    data = base64.b64encode(image_png).decode("utf-8")
    #graph = mpld3.fig_to_html(fig)
    buf.close()
    context['graph'] = data

    return render(request, 'seno.html', context)


def hello(request):
    # Generate the figure **without using pyplot**.
    fig = plt.figure()
    ax = fig.subplots()
    ax.plot([1, 2])
    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("utf-8")
    context = {'graph': data}
    return render(request, 'home.html', context)
