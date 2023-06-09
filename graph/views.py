from django.shortcuts import render
from django.http import HttpResponse
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import plotly.graph_objects as go

import math as mt
import mpld3

import base64
from io import BytesIO


# Create your views here.

def graph(request):
    context = dict()
    form_data = request.GET.dict()
    if(request.GET):
        form_data = request.GET.dict()
        context['tipo'] = (form_data.get('grafica'))
        if not form_data.get('frq') or form_data.get('frq') == 0:
            context['frq'] = 1
        else:
            context['frq'] = int(form_data.get('frq'))

        if not form_data.get('amp') or form_data.get('amp') == 0:
            context['amp'] = 1
        else:
            context['amp'] = int(form_data.get('amp'))
        
        if not form_data.get('fase'):
            context['fase'] = 0
        else:
            context['fase'] = int(form_data.get('fase'))
    else:
        if form_data =={}:
            context['frq'] = 1
            context['amp'] = 1
            context['fase'] = 0
            context['tipo'] = 'seno'
    

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

    var = np.arange(0, 11, 0.1)
    ax = move_spines()
    ax = fig.subplots()
    if context['tipo'] == 'seno':
        ax.plot(var,[context['amp'] *seno(( i - context['fase'] ) * context['frq']) for i in var], label= 'Seno')
        ax.grid()    
    
    elif context['tipo'] == 'cuadrada':
        t = np.linspace(0, 1, 1000, endpoint=True)
        fig = plt.figure()
        ax = move_spines()
        ax = fig.subplots()
        ax.plot(t, signal.square(2 * np.pi * 2 * t), drawstyle='steps-mid')
    
    
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



def cap(request):

    def nyquist(b, m):
        """
            funcion que devuelve la capacidad de uncanal en funcion de la formular de nyquist
        """
        return 2 * b * mt.log2(m)
    

    def shanon(b,m):
        """
            funcion que devuelve la capacidad de uncanal en funcion de la formular de Shanon
        """
        return b * mt.log2(m + 1)
    

    context = dict()
    form_data = request.GET.dict()
    if(request.GET):
        form_data = request.GET.dict()
        context['tipo'] = (form_data.get('grafica'))
        if not form_data.get('canal') or form_data.get('canal') == 0:
            context['canal'] = 1
        else:
            context['canal'] = int(form_data.get('canal'))

        if not form_data.get('ancho_banda') or form_data.get('ancho_banda') == 0:
            context['ancho_banda'] = 1
        else:
            context['ancho_banda'] = int(form_data.get('ancho_banda'))
        
        if not form_data.get('capa'):
            context['capa'] = 0
        else:
            if context['tipo'] == 'nys':
                context['capa'] = nyquist( context['ancho_banda'], context['canal'])
            else:
                context['capa'] = shanon( context['ancho_banda'], context['canal'])
    else:
        if form_data =={}:
            context['canal'] = 1
            context['ancho_banda'] = 50
            context['capa'] = nyquist( context['ancho_banda'], context['canal'])
            context['tipo'] = 'nys'

    
    def move_spines():
        fix, ax = plt.subplots()
        for spine in ["left", "bottom"]:
            ax.spines[spine].set_position("zero")

        for spine in ["right", "top"]:
            ax.spines[spine].set_color("none")

        return ax


    fig = plt.figure()
    var = np.arange(0, context['ancho_banda'], 1)
    ax = move_spines()
    ax = fig.subplots()


    if context['tipo'] == 'nys':
        ax.plot(var,[nyquist(i, context['canal']) for i in var], label= 'Nyquist')
        ax.grid()    
    
    elif context['tipo'] == 'sha':
        ax.plot(var,[shanon(i, context['canal']) for i in var], label= 'Nyquist')
        ax.grid()
    

    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    image_png = buf.getvalue()
    # Embed the result in the html output.
    data = base64.b64encode(image_png).decode("utf-8")
    #graph = mpld3.fig_to_html(fig)
    buf.close()
    context['graph'] = data

    return render(request, 'capacidadCanal.html', context)


def signals(request):

    def nrzl(dic):
        voltage = []
        for bit in dat:
            if bit == '0':
                bit = '1'
            else:
                bit = '-1'
            voltage.extend([int(bit), int(bit)])
        return voltage
    
    
    def nrzi(flujo):
        voltage = []
        first = True
        bit_ant = False
        for i in range(len(flujo)):
          if first:
            first = False
            if int(flujo[i])==0:
              bit = 1
              bit_ant = bit
            else:
              bit = -1
            voltage.extend([int(bit), int(bit)])
          else:
            if int(flujo[i]) == 1:
              if int(bit_ant) == 1:
                bit = -1
                bit_ant = bit
              else:
                bit = 1
                bit_ant = bit
              voltage.extend([int(bit), int(bit)])
            else:
              voltage.extend([int(bit), int(bit)])

        return voltage

    def bipolar(flujo):
        bit_ant = 0
        bit = 0
        voltage =[]
        for i in range(len(flujo)):
            if int(flujo[i]) == 0:
                bit = 0
            else:
                if bit_ant == 1 :
                    bit = -1
                    bit_ant = -1
                else:
                    bit = 1
                    bit_ant = 1 

            voltage.extend([int(bit), int(bit)])
        return voltage
    
    def pseudo(flujo):
        bit_ant = 0
        bit = 0
        voltage =[]
        for i in range(len(flujo)):
            if int(flujo[i]) == 1:
                bit = 0
            else:
                if bit_ant == 1 :
                    bit = -1
                    bit_ant = -1
                else:
                    bit = 1
                    bit_ant = 1 

            voltage.extend([int(bit), int(bit)])
        return voltage
    
    def man(flujo):
        
        voltage = []
        for bit in flujo:
            if bit == '0':
                voltage.extend(['1', '-1'])
            else:
                voltage.extend(['-1', '1'])
            
            #voltage.extend([int(bit), int(bit)] )
        #voltage = [1, 1, -1, -1, -1, 1.5, 1, 1, -1, -1, -1, -1, -1, -1, 1, 1]
        return voltage


    def man_d(flujo):
        code = []
        prev_bit = '0'
        for bit in flujo:
            if bit == '0':
                if prev_bit == '0':
                    code.extend(['1', '-1'])
                else:
                    code.extend(['-1', '1'])
            else:
                if prev_bit == '0':
                    code.extend(['-1', '1'])
                else:
                    code.extend(['1', '-1'])
            prev_bit = bit
        return code



    # Crear una lista de valores de tiempo
    def time_graf(dat):
        time = []
        for i in range(len(dat)):
            time.extend([(i),( i + 1)])
        return time

    def time_man_graf(voltage):
        dato = []
        time = []
        for i, bit in enumerate(voltage):
            dato.extend([int(bit), int(bit)])
            time.extend([i, i + 1])
        return time, dato
    
    def time_man_d_graf(voltage):
        dato = []
        time = []
        vol = 0
        for i, bit in enumerate(voltage):
            if bit == 0:
                vol = -vol
            dato.extend([int(bit), int(bit)])
            time.extend([i, i + 1])
        return time, dato

    context = dict()

    form_data = request.GET.dict()
    context['tipo'] = (form_data.get('grafica'))
    context['flujo'] = form_data.get('flujo')
    if request.GET:
        if len(context['flujo']) == 0:
            context['error'] = "Flujo de datos Errorneo"
        elif '2' in context['flujo'] or '3' in context['flujo'] or '4' in context['flujo'] or '5' in context['flujo'] or '6' in context['flujo'] or '7' in context['flujo'] or '8' in context['flujo'] or '9' in context['flujo'] in context['flujo']:
              context['error'] = "Flujo de datos Errorneo solo se perminten 1 y 0"
        else:
            dat = []
            for b in context['flujo']:
                dat.append(b)
        if not 'error' in context.keys():
            
            time = time_graf(dat)

            # Ejecuta la Función según el metodo elegido
            if context['tipo'] == 'nrzl':
                voltage = nrzl(dat)
                title_var='Flujo de Datos NRZ-L'
            elif context['tipo'] == 'nrzi':
                voltage = nrzi(dat)
                title_var='Flujo de Datos NRZ-I'
            elif context['tipo'] == 'b_ami':
                voltage = bipolar(dat)
                title_var='Flujo de Datos BIPOLAR-AMI'
            elif context['tipo'] == 'pseudo':
                voltage = pseudo(dat)
                title_var='Flujo de Datos PSEUDOTERNARIO'
            elif context['tipo'] == 'man':
                voltage = man(dat)
                title_var='Flujo de Datos MANCHESTER'
                time, voltage = time_man_graf(voltage)
            else:
                voltage = man_d(dat)
                title_var='Flujo de Datos MANCHESTER DIFERENCIAL'
                time, voltage = time_man_d_graf(voltage)
            
            
            
            # Crear el gráfico
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=time, y=voltage, mode='lines', line=dict(shape='hv')))
            fig.update_layout(
                xaxis_title='Tiempo',
                yaxis_title='Voltaje',
                title=title_var,
                yaxis=dict(range=[-1.5, 1.5]),
                showlegend=False,
                template='plotly_white'
            )

            plot_div = fig.to_html(full_html=False)


            context['graph'] = plot_div
           

    return render(request, 'signals.html', context)