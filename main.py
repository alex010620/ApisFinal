import sqlite3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {'Sistema': 'Fast Hospital'}



# Inicio de session Solo se mostraran los pacientes registrados por el doctor que los registro...

@app.get("/api/iniciar/{correo}/{clave}")
def create_tuple(correo: str, clave: str):
    my_list = []
    Email = ""
    Passw = ""
    nombre = ""
    conexion = sqlite3.connect("Hospital_Fast.s3db")
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT idDoctor, Email, Clave, Sexo,Nombre FROM Doctores WHERE Email = '" + correo + "' and Clave = '" + clave + "'")
    contenido1 = cursor.fetchall()
    conexion.commit()
    for a in contenido1:
        idDoctor = a[0]
        Email = a[1]
        Passw = a[2]
        Sexo = a[3]
        nombre = a[4]
    if correo == Email and clave == Passw:
        cursor.execute(
            "SELECT Cedula, Nombre, Apellido, Tipo_Sangre, Email, Sexo, Fecha_Nacimiento, Alergias, Foto,Zodiaco,idPaciente FROM Pacientes WHERE idDoctor = " + str(
                idDoctor) + " ")
        contenido = cursor.fetchall()
        conexion.commit()
        for i in contenido:
            my_list.append({"Datos del doctor": True,'idPaciente':i[10], 'doctor': idDoctor, 'Sexo': Sexo, "Nombre": nombre,
                            "Datos del paciente": True, 'CedulaPaciente': i[0], 'NombrePaciente': i[1],
                            'ApellidoPaciente': i[2], 'Tipo_SangrePaciente': i[3], 'EmailPaciente': i[4],
                            'SexoPaciente': i[5], 'Fecha_NacimientoPaciente': i[6], 'AlergiasPaciente': i[7],
                            'Foto': i[8], 'Zodiaco': i[9]})
        if my_list == []:
            return {"respuesta": "Bienvenido " + nombre + "", "Nombre": nombre, "id": idDoctor,"pacientes":[]}
        else:
            return{"respuesta": "Bienvenido " + nombre + "", "Nombre": nombre, "id": idDoctor,"Sexo": Sexo,"pacientes":my_list}
    else:
        return {'Ok': False}


# Consulta para Visitas por fecha, podrá seleccionar una fecha y saldrá los pacientes que visitaron en esa fecha.

@app.get("/api/fecha/{fecha}")
def fecha(fecha: str):
    datos = []
    conexion = sqlite3.connect("Hospital_Fast.s3db")
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT Paciente,Fecha,Motivo_Consulta,Numero_Seguro,Monto_Pagado,Diagnostico,Nota FROM Consulta WHERE Fecha = '" + fecha + "'")
    contenido = cursor.fetchall()
    conexion.commit()
    for i in contenido:
        datos.append(
            {"Paciente": i[0], "Fecha": i[1], "Motivo_Consulta": i[2], "Numero_Seguro": i[3], "Monto_Pagado": i[4],
             "Diagnostico": i[5], "Nota": i[6]})
    return datos


# Reporte de pacientes con cantidad de visitas, aparecerá un listado con todos los pacientes registrados y al lado la cantidad de consultas que ha hecho ese paciente.

@app.get("/api/idDoctor/{idDoctor}")
def ConsultaCantidad(idDoctor: str):
    datos = []
    conexion = sqlite3.connect("Hospital_Fast.s3db")
    cursor = conexion.cursor()
    sql = "SELECT D.idDoctor, p.Cedula, p.Nombre, p.Apellido,p.Email,count(c.idPaciente) As Cantidad FROM Pacientes as p INNER JOIN Consulta as c on p.idPaciente = c.idPaciente INNER JOIN Doctores as D on D.idDoctor = c.idDoctor WHERE c.idDoctor = " + idDoctor + " GROUP by c.Paciente"
    cursor.execute(sql)
    contenido = cursor.fetchall()
    conexion.commit()
    for i in contenido:
        datos.append({"Cedula": i[1], "Nombre": i[2], "Apellido": i[3], "Email": i[4], "Cantidad": i[5]})
    return datos


# Reporte zodiacal, aparecerá un listado de todos los pacientes cedula, nombre, apellido y signo zodiacal.

@app.get("/api/zodiaco/{idDoctor}")
def SignoZodiacal(idDoctor: str):
    datos = []
    conexion = sqlite3.connect("Hospital_Fast.s3db")
    cursor = conexion.cursor()
    sql = "SELECT Cedula, Nombre, Apellido, Zodiaco FROM Pacientes WHERE idDoctor = " + idDoctor + ""
    cursor.execute(sql)
    contenido = cursor.fetchall()
    conexion.commit()
    for i in contenido:
        datos.append({"Cedula": i[0], "Nombre": i[1], "Apellido": i[2], "Zodiaco": i[3]})
    return datos


# Registro de Doctores

@app.get("/api/crear/{nombre}/{correo}/{clave}/{sexo}")
def crear(nombre: str, correo: str, clave: str, sexo: str):
    try:
        pEmail = ""
        conexion = sqlite3.connect('Hospital_Fast.s3db')
        registro = conexion.cursor()
        registro.execute("Select Email from Doctores where Email = '" + correo + "'")
        contenido = registro.fetchall()
        for i in contenido:
            pEmail = i[0]
        if correo == pEmail:
            return {"respuesta": "El usuario con correo " + correo + " ya existe...", "Ok": False}
        else:
            usuario = (nombre, correo, clave, sexo)
            sql = '''INSERT INTO Doctores(Nombre,Email,Clave,Sexo)VALUES(?,?,?,?)'''
            registro.execute(sql, usuario)
            conexion.commit()
            return {"respuesta": "Los datos fueros registrados exitosamente", "Ok": True}
    except TypeError:
        return {"respuesta": "No se pudieron registrar los datos", "Ok": False}


# Registro de consulta

@app.get("/api/Consulta/{idPaciente}/{idDoctor}/{Paciente}/{Fecha}/{Motivo_Consulta}/{Numero_Seguro}/{Monto_Pagado}/{Diagnostico}/{Nota}/{Foto_Evidencia}")
def Consulta(idPaciente: str, idDoctor: str, Paciente: str, Fecha: str, Motivo_Consulta: str, Numero_Seguro: int,
             Monto_Pagado: int, Diagnostico: str, Nota: str, Foto_Evidencia: str):
    try:
        conexion = sqlite3.connect('Hospital_Fast.s3db')
        cursor = conexion.cursor()
        usuario = (
        idPaciente, idDoctor, Paciente, Fecha, Motivo_Consulta, Numero_Seguro, Monto_Pagado, Diagnostico, Nota,
        Foto_Evidencia)
        sql = '''INSERT INTO Consulta(idPaciente,idDoctor,Paciente,Fecha,Motivo_Consulta,Numero_Seguro,Monto_Pagado,Diagnostico,Nota,Foto_Evidencia)VALUES(?,?,?,?,?,?,?,?,?,?)'''
        cursor.execute(sql, usuario)
        conexion.commit()
        return {"respuesta": "Los datos fueros registrados exitosamente"}
    except:
        return {"respuesta": "No se pudieron registrar los datos"}


@app.get("/api/SeleccionarConsulta/{idPaciente}")
def SeleccionarConsulta(idPaciente: str):
    try:
        lista=[]
        conexion = sqlite3.connect('Hospital_Fast.s3db')
        cursor = conexion.cursor()
        cursor.execute("SELECT Fecha,Motivo_Consulta,Numero_Seguro,Monto_Pagado,Diagnostico,Nota,Foto_Evidencia, idConsulta FROM Consulta WHERE idPaciente = '"+idPaciente+"'")
        contenido= cursor.fetchall()
        conexion.commit()
        for i in contenido:
            lista.append({"fecha":i[0],"motivoConsulta":i[1],"numeroSeguro":i[2],"montoPagado":i[3],"diagnostico":i[4],"nota":i[5],"evidencia":i[6], "idConsulta":i[7]})
        if lista == []:
            return {"respuesta":"El paciente no tiene citas generadas"}
        else:
            return lista
    except:
        return {"respuesta": "No se pudieron estraer los datos"}


@app.get("/api/SeleccionarConsultaUnica/{idConsulta}")
def SeleccionarConsultaUnica(idConsulta: str):
    try:

        conexion = sqlite3.connect('Hospital_Fast.s3db')
        cursor = conexion.cursor()
        cursor.execute("SELECT Fecha,Motivo_Consulta,Numero_Seguro,Monto_Pagado,Diagnostico,Nota,Foto_Evidencia, idConsulta FROM Consulta WHERE idConsulta = '"+idConsulta+"'")
        contenido= cursor.fetchall()
        conexion.commit()
        for i in contenido:
            lista = {"fecha":i[0],"motivoConsulta":i[1],"numeroSeguro":i[2],"montoPagado":i[3],"diagnostico":i[4],"nota":i[5],"evidencia":i[6], "idConsulta":i[7]}
        if lista == {}:
            return {"respuesta":"El paciente no tiene citas generadas"}
        else:
            return lista
    except:
        return {"respuesta": "No se pudieron estraer los datos"}


# Actualizar Consulta Paciente

@app.get(
    "/api/ActualizarConsulta/{idConsulta}/{Paciente}/{Fecha}/{Motivo_Consulta}/{Numero_Seguro}/{Diagnostico}/{Monto_Pagado}/{Nota}/{Foto_Evidencia}")
def ActualizarConsulta(idConsulta: str, Paciente: str, Fecha: str, Motivo_Consulta: str, Numero_Seguro: str,
                       Monto_Pagado: str, Diagnostico: str, Nota: str, Foto_Evidencia: str):
    try:
        conexion = sqlite3.connect('Hospital_Fast.s3db')
        cursor = conexion.cursor()
        sql2 = "UPDATE Consulta SET Paciente='" + Paciente + "',Fecha='" + Fecha + "',Motivo_Consulta='" + Motivo_Consulta + "',Monto_Pagado='" + Monto_Pagado + "',Numero_Seguro='" + Numero_Seguro + "',Diagnostico='" + Diagnostico + "',Nota='" + Nota + "',Foto_Evidencia='" + Foto_Evidencia + "' WHERE idConsulta = '" + idConsulta + "'"
        cursor.execute(sql2)
        conexion.commit()
        return {"respuesta": "Los datos fueros registrados exitosamente"}
    except EnvironmentError:
        return {"respuesta": "No se pudieron actualizar los datos"}


'''
Registro de pacientes
'''


@app.get(
    "/api/Pacientes/{idDoctor}/{Cedula}/{Foto}/{Nombre}/{Apellido}/{Tipo_Sangre}/{Email}/{Sexo}/{Fecha_Nacimiento}/{Alergias}/{Zodiaco}")
def crearPaciente(idDoctor: str, Cedula: str, Foto: str, Nombre: str, Apellido: str, Tipo_Sangre: str, Email: str,
                  Sexo: str, Fecha_Nacimiento: str, Alergias: str, Zodiaco: str):
    try:
        conexion = sqlite3.connect('Hospital_Fast.s3db')
        registro = conexion.cursor()
        usuario = (
        idDoctor, Cedula, Foto, Nombre, Apellido, Tipo_Sangre, Email, Sexo, Fecha_Nacimiento, Alergias, Zodiaco)
        sql = '''INSERT INTO Pacientes(idDoctor,Cedula,Foto,Nombre,Apellido,Tipo_Sangre,Email,Sexo,Fecha_Nacimiento,Alergias,Zodiaco)VALUES(?,?,?,?,?,?,?,?,?,?,?)'''
        registro.execute(sql, usuario)
        conexion.commit()
        return {"respuesta": "Los datos fueros registrados exitosamente"}
    except TypeError:
        return {"respuesta": "No se pudieron registrar los datos"}


# Actualizar paciente................

@app.get(
    "/api/ActualizarPaciente/{idPaciente}/{Cedula}/{Foto}/{Nombre}/{Apellido}/{Tipo_Sangre}/{Email}/{Sexo}/{Fecha_Nacimiento}/{Alergias}/{Zodiaco}")
def ActualizarPaciente(idPaciente: str, Cedula: str, Foto: str, Nombre: str, Apellido: str, Tipo_Sangre: str,
                       Email: str, Sexo: str, Fecha_Nacimiento: str, Alergias: str, Zodiaco: str):
    try:
        conexion = sqlite3.connect('Hospital_Fast.s3db')
        registro = conexion.cursor()
        sql = "UPDATE Pacientes SET Cedula='" + Cedula + "',Foto='" + Foto + "',Nombre='" + Nombre + "',Apellido='" + Apellido + "',Tipo_Sangre='" + Tipo_Sangre + "',Email='" + Email + "',Sexo='" + Sexo + "',Fecha_Nacimiento='" + Fecha_Nacimiento + "',Alergias='" + Alergias + "',Zodiaco='" + Zodiaco + "' WHERE idPaciente=" + idPaciente + ""
        registro.execute(sql)
        conexion.commit()
        return {"respuesta": "Los datos fueros actualizados exitosamente"}
    except TypeError:
        return {"respuesta": "No se pudieron actualizados los datos"}


# Modificacion del Doctor

@app.get("/api/modificar/{nombre}/{correo}/{token}")
def modificar(nombre: str, correo: str, token: str):
    try:
        conexion = sqlite3.connect('Hospital_Fast.s3db')
        cursor = conexion.cursor()
        update = "UPDATE Doctores SET Nombre = '" + nombre + "', Email = '" + correo + "' WHERE idDoctor = '" + token + "'"
        cursor.execute(update)
        conexion.commit()
        return {"respuesta": "Se modificaron los datos"}
    except TypeError:
        return {"respuesta": "No se pudieron modificar los datos"}


# Modificacion de las credenciales del doctor

@app.get("/api/ModClave/{clave_old}/{token}/{new_clave}")
def modClave(clave_old: str, token: str, new_clave: str):
    try:
        conexion = sqlite3.connect('Hospital_Fast.s3db')
        cursor = conexion.cursor()
        select = "SELECT * FROM Doctores WHERE  idDoctor='" + token + "'"
        cursor.execute(select)

        if cursor.fetchall()[0][3] != clave_old:
            return {"ok": False, "respeusta": "Clave Incorrecta"}

        updat = "UPDATE Doctores SET Clave ='" + new_clave + "' WHERE Clave = '" + clave_old + "' and idDoctor ='" + token + "'"
        cursor.execute(updat)
        conexion.commit()
        return {"ok": True, "respuesta": "Se modificaron los datos"}
    except TypeError:
        return {"ok": False, "respuesta": "No se pudieron modificar los datos"}