
from ctypes.wintypes import tagRECT
from tkinter import image_names
from flask import Flask, render_template, url_for, redirect, request, session, jsonify, flash, get_flashed_messages
from flask.helpers import flash
from flask_mysqldb import MySQL
import pandas as pd
import os
from werkzeug.utils import secure_filename
import json

app=Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'contacts'
mysql = MySQL(app)


app.secret_key="applogin"

app.config["IMAGE"] = "static\docs"
app.config["FACTURAS"] = "static\Facturas"
app.config["EXCEL"] = "static\excel"


'''cur = mysql.connection.cursor()
cur.execute('SELECT * FROM prueba_3')
result_list = cur.fetchall() 


fields_list = cur.description   # sql key name
#print("header--->",fields)
cur.close()



    # main part
column_list = []
for i in fields_list:
    column_list.append(i[0])

    # print("colume list  -->", column_list)

jsonData_list = []
for row in result_list:
    data_dict = {}
    for i in range(len(column_list)):
        data_dict[column_list[i]] = row[i]
    #把data_dict 加入返回的jsonData_list列表中
    jsonData_list.append(data_dict)

tabla= (jsonify({'space': jsonData_list}))'''



@app.route('/') ######################################################################
def index():
    session.clear()
    return render_template("index.html")

@app.route('/login-ascesores',methods = ["GET","POST"]) ######################################################################
def login_ascesores():

    if not session:
        if request.method == 'POST':
            name = request.form['nmUserNamea']
            passw = request.form['nmPassa']

            valor = login(name,passw)
            print(valor)

            if valor[0] >= 1:           ##  Indica que existe la cuenta y tiene permisos para entrar a ascesores
                session['nombre'] = name
                session['estado'] = valor[1]

                return redirect(url_for('ascesores', estados = session['estado']))

            else:
                return redirect(url_for('login_ascesores'))        ##  La cuenta no es valida y no entrará a ascesores

        return render_template('login-ascesores.html')

    else:
        return redirect(url_for('ascesores', estados = session['estado']))

@app.route('/login-ventas',methods = ["GET","POST"]) ######################################################################
def login_ventas():

    if not session:
        if request.method == 'POST':
            name = request.form['nmUserNamea']
            passw = request.form['nmPassa']

            valor = login(name,passw)

            if valor[0] >= 1:           ##  Indica que existe la cuenta y tiene permisos para entrar a ventas
                session['nombre'] = name
                session['estado'] = valor[1]

                return redirect(url_for('ventas', estados = session['estado']))

            else:
                return redirect(url_for('login_ventas'))        ##  La cuenta no es valida y no entrará a ventas

        return render_template('login-ventas.html')

    else:
        return redirect(url_for('ventas', estados = session['estado']))
    
@app.route('/login-admin',methods = ["GET","POST"]) ######################################################################
def login_admin():

    if not session:
        if request.method == 'POST':
            name = request.form['nmUserNamea']
            passw = request.form['nmPassa']

            valor = login(name,passw)

            if valor[0] >= 2:       ## indica que la cuenta es administrador o superior y puede entrar a admin
                session['nombre'] = name
                session['estado'] = valor[1]

                
                return redirect(url_for('admin'))

            else:                         ##  indica que la cuenta no existe o es de rango inferior y no entrará a admin
                  return redirect(url_for('login_admin'))

        return render_template('login-administrador.html')

    elif session['estado'] == "administrador":
        return redirect(url_for('admin'))

    else:
        return redirect(url_for('ventas', estados = session['estado']))

@app.route('/login-bancos',methods = ['GET', 'POST'])
def login_bancos():

    if not session:
        if request.method == 'POST':
            name = request.form['nmUserNamea']
            passw = request.form['nmPassa']

            valor = login(name,passw)

            if valor[0] >= 2:
                session['nombre'] = name
                session['estado'] = valor[1]
                return redirect(url_for('bancos'))
            else:
                return redirect(url_for('login_bancos'))

        return render_template('login-bancos.html')
        
    elif session ['estado'] == 'administrador':
        redirect(url_for('bancos'))
    else:
        return redirect(url_for('ventas'), estados = session['estado'])


@app.route('/login-graficas',methods = ["GET","POST"]) ######################################################################
def login_graficas():

    if not session:
        if request.method == 'POST':
            name = request.form['nmUserNamea']
            passw = request.form['nmPassa']

            valor = login(name,passw)

            if valor[0] >= 2:
                session['nombre'] = name
                session['estado'] = valor[1]

                
                return redirect(url_for('graficas'))

            else:
                return redirect(url_for('login_graficas'))

        return render_template('login-graficas.html')

    elif session['estado'] == "administrador":
        return redirect(url_for('graficas'))

    else:
        return redirect(url_for('ventas', estados = session['estado']))

@app.route('/login-facturas',methods = ["GET","POST"]) ######################################################################
def login_facturas():

    if not session:
        if request.method == 'POST':
            name = request.form['nmUserNamea']
            passw = request.form['nmPassa']

            valor = login(name,passw)

            if valor[0] >= 1:           ##  Indica que existe la cuenta y tiene permisos para entrar a ventas
                session['nombre'] = name
                session['estado'] = valor[1]

                return redirect(url_for('facturas'))

            else:
                return redirect(url_for('login-facturas'))        ##  La cuenta no es valida y no entrará a ventas

        return render_template('login-facturas.html')

    else:
        return redirect(url_for('facturas'))



####################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################

@app.route('/delete/<string:id>/<fechainicial>/<fechafinal>') ######################################################################
def delete_contact(id,fechainicial,fechafinal):
    if not session:
        return redirect(url_for('login_admin'))

    else:
        priv = privilegios(session['nombre'])       
        if priv[0] <= 1:                         ### se revisan los privilegios antes de dar la orden de eliminar
            return redirect(url_for('ventas', estados = priv[1]))
        
        else:
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM prueba_3 WHERE id = {}'.format(id))
            data = cur.fetchall()

            number = data[0][4]
            try: 
                path1 = os.path.join(app.config["IMAGE"], "{}_ine.pdf".format(number))
                os.remove(path1)
            except:
                print("archivo no encontrado")
            
            try:
                path2 = os.path.join(app.config["IMAGE"], "{}_solicitud.pdf".format(number))
                os.remove(path2)
            except:
                print("archivo no encontrado")

            try:
                path3 = os.path.join(app.config["IMAGE"], "{}_estado_cuenta.pdf".format(number))
                os.remove(path3)
            except:
                print("archivo no encontrado")

            cur = mysql.connection.cursor()
            cur.execute('DELETE FROM prueba_3 WHERE id = {0}'.format(id))
            mysql.connection.commit()
            return redirect(url_for('tabla', fechainiciall = fechainicial, fechafinall = fechafinal))


@app.route('/edit/<string:id>/<fechainicial>/<fechafinal>') ######################################################################
def get_contact(id,fechainicial,fechafinal):

    if not session:
        return redirect(url_for('login_admin'))

    else:
        priv = privilegios(session['nombre'])
        if priv[0] <= 1:                ### se revisan los privilegios antes de dar la orden de editar
            return redirect(url_for('ventas', estados = priv[1]))

        else:
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM prueba_3 WHERE id = {}'.format(id))
            data = cur.fetchall()
            dicc = {
                    'usuario' : session['nombre'],
                    'fechainicial' : fechainicial,
                    'fechafinal' : fechafinal
                    }  
            return render_template('edit-contact.html',data = dicc ,contact = data[0])
        ##pendiente

@app.route('/update/<id>/<fechainicial>/<fechafinal>', methods = ['POST']) ######################################################################
def update_contact(id,fechainicial,fechafinal):

    if not session:
        return redirect(url_for('login_admin'))

    else:
        priv = privilegios(session['nombre'])
        if priv[0] <= 1:                ### se revisan los privilegios antes de dar la orden de editar
            return redirect(url_for('ventas', estados = priv[1]))

        else:
            #Obtención de datos
            if request.method == 'POST':
                ascesor = request.form['ascesor']
                nombre_cliente= request.form['nombre_cliente']
                numero_tarjeta=request.form['numero_tarjeta']
                monto = request.form['monto']
                retorno_cliente = request.form['retorno_cliente']
                retorno_ascesor = request.form['retorno_ascesor']
                banco = request.form['banco']
                clabe = request.form['clabe']
                ine = request.files['ine']
                solicitud = request.files['solicitud']
                estado = request.files['estado_cuenta']

                if (extension(ine.filename) == False) or (extension(solicitud.filename) == False) or (extension(estado.filename) == False):
                    flash("error")
                    return redirect(url_for('get_contact', id = id, fechainicial = fechainicial, fechafinal = fechafinal))

                Nine = numero_tarjeta + "_" + "ine.pdf"
                Nsolicitud = numero_tarjeta + "_" + "solicitud.pdf"
                Nestado_cuenta = numero_tarjeta + "_" + "estado_cuenta.pdf"

                ine.save(os.path.join(app.config["IMAGE"], Nine))
                solicitud.save(os.path.join(app.config["IMAGE"], Nsolicitud))
                estado.save(os.path.join(app.config["IMAGE"], Nestado_cuenta))

        #consulta SQL
                cur = mysql.connection.cursor()
                cur.execute("""
                UPDATE prueba_3 
                SET ascesor = %s,
                    nombre_cliente = %s,
                    numero_tarjeta= %s,
                    monto = %s,
                    retorno_cliente = %s,
                    retorno_ascesor = %s,
                    banco = %s,
                    clabe = %s
                    WHERE id = %s
                """, (ascesor,nombre_cliente, numero_tarjeta, monto, retorno_cliente, retorno_ascesor,banco,clabe,id))
                mysql.connection.commit()
                return redirect(url_for('tabla', fechainiciall = fechainicial, fechafinall = fechafinal))

####################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################
@app.route('/bancos', methods = ['POST', 'GET'])
def bancos():

    if not session:
        return redirect(url_for('login_bancos'))
    
    elif session['estado'] != 'administrador':
        return redirect(url_for('ventas', estado = session['estado']))

    else:
        dicc = {
            'usuario' : session['nombre']
        }
        if request.method == 'POST':
            excel_document = request.files['documento']
            id_num = request.form['id_num']
            fecha_ultima = request.form['fecha_ult']
            nombre = "excel_{}".format(fecha_ultima)
            excel_document.save(os.path.join(app.config["EXCEL"], nombre))
            path_file = ("\static\excel\{}.csv".format(nombre))
            print(path_file)
            # df = pd.read_csv(path_file)
            # print(df)




        return render_template('formulario-bancos.html',data = dicc)

@app.route('/administracion', methods = ['GET',"POST"]) ######################################################################
def admin():   

    if not session:
        return redirect(url_for('login_admin'))
    
    elif session['estado'] != 'administrador':
        return redirect(url_for('ventas', estados = session['estado']))

    else:
        dicc = {
            'usuario' : session['nombre']
        }
        if request.method == 'POST':
            fi = request.form['fi']
            ff= request.form['ff']

            if (fi!= None and ff != None):

                fii = fi.replace("-","")
                fff = ff.replace("-","")

                return redirect(url_for('tabla', fechainiciall = fii, fechafinall = fff))


        return render_template('administrador.html', data = dicc)


def extension(filename):
    if not "." in filename:
        return False
    
    ext = filename.rsplit(".",1)[1]

    if ext.upper() in ["PDF"]:
        return True
    else:
        return False

@app.route('/ascesores/<estados>', methods = ['GET',"POST"]) ######################################################################
def ascesores(estados):

    if estados != session['estado']:
        return redirect(url_for('ascesores', estados = session['estado']))

    if not session:
        return redirect(url_for('login_ascesores'))

    else:
        dicc = {
                'estados': session['estado'],
                'usuario': session['nombre']
            }
        

        if request.method == 'POST':
            ascesor = request.form['ascesor']
            nombre_cliente= request.form['nombre_cliente']
            numero_tarjeta=request.form['numero_tarjeta']
            monto = request.form['monto']
            retorno_cliente = request.form['retorno_cliente']
            retorno_ascesor = request.form['retorno_ascesor']
            banco = request.form['banco']
            clabe = request.form['clabe']
            ine = request.files['ine']
            solicitud = request.files['solicitud']
            estado = request.files['estado_cuenta']

            if (extension(ine.filename) == False) or (extension(solicitud.filename) == False) or (extension(estado.filename) == False):
                flash("extension incorrecta")
                return redirect(url_for('ascesores', estados = session['estado']))

            Nine = numero_tarjeta + "_" + "ine.pdf"
            Nsolicitud = numero_tarjeta + "_" + "solicitud.pdf"
            Nestado_cuenta = numero_tarjeta + "_" + "estado_cuenta.pdf"

            ine.save(os.path.join(app.config["IMAGE"], Nine))
            solicitud.save(os.path.join(app.config["IMAGE"], Nsolicitud))
            estado.save(os.path.join(app.config["IMAGE"], Nestado_cuenta))

            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO prueba_3(ascesor, nombre_cliente, numero_tarjeta, monto, retorno_cliente, retorno_ascesor, banco,clabe) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
            (ascesor,nombre_cliente,numero_tarjeta,monto,retorno_cliente,retorno_ascesor,banco,clabe))
            mysql.connection.commit()

            #cur = mysql.connection.cursor()
            #cur.execute('INSERT INTO prueba_3(ascesor, nombre_cliente, numero_tarjeta, monto, retorno_cliente, retorno_ascesor, banco,#clabe,ine,solicitud,estado_de_cuenta) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            #(ascesor,nombre_cliente,numero_tarjeta,monto,retorno_cliente,retorno_ascesor,banco,clabe,Nine,Nsolicitud,Nestado_cuenta))
            #mysql.connection.commit()

        return render_template('ascesores.html', data = dicc)

@app.route('/ventas/<estados>', methods = ['GET',"POST"]) ######################################################################
def ventas(estados):

    if estados != session['estado']:
        return redirect(url_for('ventas', estados = session['estado']))

    if not session:
        return redirect(url_for('login_ventas'))

    else:
        dicc = {
                'estados': session['estado'],
                'usuario': session['nombre']
            }
        

        if request.method == 'POST':
            fecha_venta= request.form['fecha_venta'].replace("-","")
            fecha_cobro= request.form['fecha_cobro'].replace("-","")
            numero_orden=request.form['numero_orden']
            numero_credito = request.form['numero_credito']
            nombre_cliente = request.form['nombre_cliente']
            monto_vale = request.form['monto_vale']
            diferencia = request.form['diferencia']
            fecha_diferencia = request.form['fecha_diferencia'].replace("-","")
            fecha_diferencia_ilda = request.form['fecha_diferencia_ilda'].replace("-","")
            forma_pago = request.form['forma_pago']
            vendedora = request.form['vendedora']
            numero_factura = request.form['numero_factura']
            fecha_entrega = request.form['fecha_entrega'].replace("-","")
            observaciones = request.form['observaciones']
            print(fecha_venta,fecha_cobro,numero_orden,numero_credito,nombre_cliente,monto_vale,diferencia,fecha_diferencia,fecha_diferencia_ilda,forma_pago,vendedora,numero_factura,fecha_entrega,observaciones)

            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO ventas(Fecha_venta, Fecha_cobro, Numero_orden, Numero_credito, Nombre_cliente, Monto_vale, Diferencia, Fecha_de_diferencia_pagada, Fecha_de_diferencia_pagada_ilda, Forma_pago, Vendedora, Numero_Factura, Fecha_entrega, Observaciones) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            (fecha_venta,fecha_cobro,numero_orden,numero_credito,nombre_cliente,monto_vale,diferencia,fecha_diferencia,fecha_diferencia_ilda,forma_pago,vendedora,numero_factura,fecha_entrega,observaciones))
            mysql.connection.commit()

            #cur = mysql.connection.cursor()
            #cur.execute('INSERT INTO prueba_3(ascesor, nombre_cliente, numero_tarjeta, monto, retorno_cliente, retorno_ascesor, banco,#clabe,ine,solicitud,estado_de_cuenta) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            #(ascesor,nombre_cliente,numero_tarjeta,monto,retorno_cliente,retorno_ascesor,banco,clabe,Nine,Nsolicitud,Nestado_cuenta))
            #mysql.connection.commit()

        return render_template('ventas.html', data = dicc)        
                
@app.route('/doc/<numero>')   ######################################################################
def imagenes(numero):

    dicc = {
        "url" : numero
    }

    return render_template('doc.html', data = dicc)

@app.route('/graficas', methods = ['GET','POST'])   ######################################################################
def graficas():

    if not session:
        return redirect(url_for('login_graficas'))
    
    elif session['estado'] != 'administrador':
        return redirect(url_for('ventas', estados = session['estado']))

    else:
        dicc = {
                'usuario': session['nombre']
            }

        return render_template('menu-graficas.html', data = dicc)

        
@app.route('/tabla/<fechainiciall>/<fechafinall>') ######################################################################
def tabla(fechainiciall,fechafinall): 

    if not session:
        return redirect(url_for('login_graficas'))
    
    elif session['estado'] != 'administrador':
        return redirect(url_for('ventas', estados = session['estado']))

    else:
        dicc = {
            'usuario' : session['nombre'],
            'fechainicial' : fechainiciall,
            'fechafinal' : fechafinall
            }  

        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM prueba_3 WHERE fecha BETWEEN {} AND {}'.format(fechainiciall,fechafinall))
        data = cur.fetchall() 

        fechas = {
            'fecha_inicial' : fecha(fechainiciall),
            'fecha_final' : fecha(fechafinall)
        }

        return render_template('tabla.html', data = dicc, contacts = data, FECHAS = fechas)

@app.route('/facturas', methods = ['GET',"POST"]) ######################################################################
def facturas():

    if not session:
        return redirect(url_for('login_ventas'))

    else:
        dicc = {
                'usuario': session['nombre']
            }
        

        return render_template('facturas.html', data = dicc)


##########################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################

@app.route('/subir-factura-b', methods = ['GET',"POST"])
def subir_factura_b():
    if not session:
        return redirect(url_for('login_facturas'))
    
    elif session['estado'] != 'administrador':
        return redirect(url_for('facturas'))  ## descargar facturas

    else:
        dicc = {
            'usuario' : session['nombre']
        }
        if request.method == 'POST':
            number_target = request.form['number_target']

            return redirect(url_for('subir_factura', target = number_target))


        return render_template('subir-factura-b.html', data = dicc)

@app.route('/subir-factura/<target>', methods = ['GET',"POST"])  #######################################################################
def subir_factura(target):

    if not session:
        return redirect(url_for('login_facturas'))
    
    elif session['estado'] != 'administrador':
        return redirect(url_for('facturas'))  ## descargar facturas

    else:
        dicc = {
            'usuario' : session['nombre'],
            'target' : target
        }
        if request.method == 'POST':
            factura = request.files['factura']

            if (extension(factura.filename) == False):
                flash("extension incorrecta")
                return redirect(url_for('subir_factura', target = target))

            Nfactura = target + "_" + "factura.pdf"

            factura.save(os.path.join(app.config["FACTURAS"], Nfactura))
        

        return render_template('subir-factura.html', data = dicc)


@app.route('/descargar-factura-b', methods = ['GET',"POST"])
def descargar_factura_b():

    if not session:
        return redirect(url_for('login_facturas'))

    else:
        dicc = {
            'usuario' : session['nombre']
        }
        if request.method == 'POST':
            number_target = request.form['number_target']

            return redirect(url_for('descargar_factura', target = number_target))


        return render_template('descargar-facturas-b.html', data = dicc)


@app.route('/desargar-factura/<target>')  #######################################################################
def descargar_factura(target):

    if not session:
        return redirect(url_for('login_facturas'))

    else:
        dicc = {
            'usuario' : session['nombre'],
            'target' : target
        }
        

        return render_template('descargar-facturas.html', data = dicc)

##########################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################

@app.route('/salir') ######################################################################
def salir():
    return redirect(url_for('index'))

@app.route('/dashboard', methods = ['POST', 'GET'])
def dashboard():

        if not session:
            return redirect(url_for('login_graficas'))
    

        else:
            dicc = {
                'usuario' : session['nombre']
            }
            if request.method == 'POST':
  
                vendedoras_seleccionadas = request.form['valores_vendedoras'].split(",")
                estados_seleccionados= request.form['valores_estados'].split(",")
                fecha_inicial = request.form['fechai'].replace("-","")
                fecha_final = request.form['fechaf'].replace("-","")
                print(vendedoras_seleccionadas)
                print(estados_seleccionados)
                print(fecha_inicial)
                print(fecha_final)
                
                
                cur = mysql.connection.cursor()
                cur.execute("SELECT * FROM historial_llamadas WHERE fecha > {} AND fecha < {}".format(fecha_inicial,fecha_final))

                data = cur.fetchall()
                
              

                mysql.connection.commit
                if len(data) ==0:
                    return render_template('sin-datos.html')
                else:
                    df = pd.DataFrame(data)

                    df_new = df[df[2].isin(estados_seleccionados)]
                    df_new = df_new[df_new[4].isin(vendedoras_seleccionadas)]

                    

                    dias = ["lunes","martes","miércoles","jueves","viernes","sábado"]
                    horas = ["8","9","10","11","12","13","14","15","16","17","18","19","20","21","22","23","0"]

                    df_new[4] = pd.Categorical(df_new[4])
                    df_new[17] = pd.Categorical(df_new[17],categories=dias,ordered=True)
                    df_new[14] = pd.Categorical(df_new[14])
                    df_new[13] = pd.Categorical(df_new[13])
                    df_new[10] = pd.Categorical(df_new[10])
                
                    categories_1 = df_new[17].cat.categories
                    categories_2 = df_new[4].cat.categories
                    categories_3 = df_new[13].cat.categories
                    categories_4 = df_new[14].cat.categories
                    categories_5 = df_new[10].cat.categories
                    
                    #######################################################
                    #ciclo for prueba
                    

                    
                    tabla_dia = []
                    tabla_grafica_depuraciones = []
                    totales_dia = []
                    tabla_valores = []
                    tabla_valores_vendedora = []
                    totales_vendedora = ["total"]
                    tabla__para_grafica_totales_por_semana = []
                    lista_valores_grupo = []
                    lista_elementos_seguimiento = []
                    lista_seguimiento = []
                    tabla_seguimiento = []
                    
                #####################################################################################
                #------Primer ciclo for que itera el numero total de empleados que coinciden con un dia de la semana y regresa una lista con 5 listas de 21 elementos
                    for dia in categories_1:
                        lista_1 = []
                        tabla_valores.append(lista_1)
                        
                        for empleada in categories_2:
                            valores = len(df[(df[17] == dia) & (df[4] == empleada)])
                            lista_1.append(valores)

                #####################################################################################
                #------Primer ciclo for que itera el numero total de empleados que coinciden con un dia de la semana y regresa una lista con 21 listas de 5 elementos
                    for empleada in categories_2:
                        lista_1 = []
                        tabla__para_grafica_totales_por_semana.append(lista_1)
                        
                        for dia in categories_1:
                            valores = len(df[(df[17] == dia) & (df[4] == empleada)])
                            lista_1.append(valores)
                
                #####################################################################################
                #------Retorna una lista con 21 listas con 6 datos cada una 
                    for empleada in categories_2:
                        lista_1 = []
                        tabla_valores_vendedora.append(lista_1)
                        
                        for dia in categories_1:
                            valores = len(df[(df[17] == dia) & (df[4] == empleada)])
                            lista_1.append(valores)

                ###############################################################
                #------------Los mismo que la primera pero con el dia de la semana al comienzo
                    for dia in categories_1:
                        lista_1 = [dia]
                        tabla_dia.append(lista_1)
                        
                        for empleada in categories_2:
                            valores = len(df[(df[17] == dia) & (df[4] == empleada)])
                            lista_1.append(valores)

                #########################################################################################
                # -------------Retorna una lista donde vienes dos listas una para numeros depurados y otra para llamadas          
                    
                    for element in categories_4:
                        lista_3 = []
                        tabla_grafica_depuraciones.append(lista_3)
                        
                        for empleada in categories_2:
                            valores = len(df[(df[14] == element) & (df[4] == empleada)])
                            lista_3.append(valores)
                ###############################################
                #------------transforma categories_2 en una lista con los elementos que contiene categories_2 esto para poder mandarlo al html sin problema
                    vendedoras = []
                    for row in categories_2:
                        vendedoras.append(row)
                    vendedoras.append("Total")


                ###############################################
                #------------transforma categories_2 en una lista con los elementos que contiene categories_2 esto para poder mandarlo al html sin problema
                    grupo = []
                    for row in categories_3:
                        grupo.append(row)
                    
                    

                #############################################
                #--------------se suman los totales que tiene la lista de valores para poder obtener los totales
                    for dia in tabla_valores:
                        suma = sum(dia)
                        totales_dia.append(suma)

                    #############################################
                #--------------se suman los totales que tiene la lista de valores para poder obtener los totales
                    for empleada in tabla_valores_vendedora:
                        suma = sum(empleada)
                        totales_vendedora.append(suma)
                    totales_dia.append(sum(totales_dia))
                #####################################################



                    tabla_con_totales = tabla_dia + [totales_vendedora]
                    i = 0
                    for lista in tabla_con_totales:
                        lista.append(totales_dia[i])
                        i+=1
                ########################################################
                    
                    tabla_totales_semana = []
                    j = 1
                    for empleada in vendedoras:
                        lista = [empleada]
                        lista.append(totales_vendedora[j])
                        j+=1
                        tabla_totales_semana.append(lista)

                ##########################################################
                ##-------------------Aquí se hará la iteración para la grafica de dona donde se necesitan los valores categoricos y cuanto es el total de cada estatus
                    for element in categories_3:
                        valores = len(df[(df[13] == element)])
                        lista_valores_grupo.append(valores)

                ##########################################################
                ##-------------------Aquí se hará la iteración para la grafica de dona donde se necesitan los valores categoricos y cuanto es el total de cada estatus
                    for element in categories_5:
                        valores = len(df[(df[10] == element)])
                        lista_elementos_seguimiento.append(valores)

                    for element in categories_5:
                        lista_seguimiento.append(element)
                    
    

                    tabla_grafica_dona = [grupo] + [lista_valores_grupo]
                    tabla_seguimiento = [lista_seguimiento] + [lista_elementos_seguimiento]
                


                    return render_template('plantilla-tres.html', data = dicc, dias = dias, datos = tabla_con_totales, grafica_seguimiento = tabla_seguimiento, vendedora = vendedoras, values_grafica = tabla_grafica_depuraciones, tabla_totales_semana = tabla_totales_semana, grafica_totales_por_semana=tabla__para_grafica_totales_por_semana, grafica_dona = tabla_grafica_dona, vendedoras_graficas = vendedoras[0:len(vendedoras)-1],totales_dia = totales_dia)
 
def error_404(error): ######################################################################
    session.clear()
    return render_template('error.html'), 404


def login(nombre,passw):        ## función para revisar que la cuenta exxista y sea valida

    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM users WHERE name="{}"'.format(nombre))
    data = cur.fetchall() 

    if len(data) == 0:
        print("No hay nada")
        return([0,'No hay'])


    else:
        if data[0][3] == passw:
            if data[0][4] == "44":
                estado = data[0][5]
                return([1,estado])

            else:
                return([2,'administrador'])

        else:
            return([0,'No hay'])

def privilegios(nombre):        ## función sólo para revisar privilegios sin recibir contraseña
    
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM users WHERE name="{}"'.format(nombre))
    data = cur.fetchall() 


    if data[0][4] == "44":
        estado = data[0][5]
        return([1,estado])

    else:
        return([2,'administrador'])


def fecha(num):         ## función para poder desplegar la fecha bonita y no con los digitos pegados

    new_num = list(num)

    año = (''.join(new_num[0:4]))
    mes = (''.join(new_num[4:6]))
    dia = (''.join(new_num[6:9]))

    fecha = [año, mes, dia]
    fecha = ('-'.join(fecha))

    return(fecha)


if __name__ == '__main__': ######################################################################
    app.register_error_handler(404, error_404)
    app.run(debug=True, port=5000)

