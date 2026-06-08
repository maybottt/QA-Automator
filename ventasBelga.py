import os
from pywinauto.application import Application
from pywinauto.keyboard import send_keys
from time import sleep
from pywinauto import Desktop

# Definimos las rutas
path_app = r'C:\Program Files (x86)\SEDNA SRL\GeCOIN plus ERP\WinVentas.exe'
dir_app = os.path.dirname(path_app) # Extrae la carpeta contenedora

print("Iniciando la aplicación con pywinauto...")
# Iniciamos la app estableciendo explícitamente su directorio de trabajo
app = Application(backend="uia").start(path_app, work_dir=dir_app)

# Esperamos unos segundos a que cargue la ventana de login
sleep(2.3)

# Opcional: En lugar de buscar en Desktop, podemos buscar la ventana directamente en la app iniciada
try:
    dialog = app.frmLogin2
    dialog.wait('visible', timeout=10)
except Exception:
    # Si la ventana se abre en un proceso independiente, volvemos al método del Desktop
    dialog = Desktop(backend='uia').frmLogin2
    dialog.wait('visible', timeout=10)

sleep(1)

# El resto de tu código de automatización...
usuario = dialog.child_window(auto_id="TxtUsuario", control_type="Edit")
clave   = dialog.child_window(auto_id="TxtClave",   control_type="Edit")

usuario.set_focus()
sleep(0.3)
send_keys("SOPORTE")
sleep(0.5)

clave.set_focus()
sleep(0.3)
send_keys("1")
sleep(0.5)

dialog.child_window(auto_id="simpleButtonIngreso", control_type="Button").click_input() 
sleep(10)

#carga la pantalla despues del login 
main = Desktop(backend="uia").window(auto_id="mainVentas")
main.wait("exists enabled visible", timeout=20)
print("Ventana Ventas encontrada")
main.child_window(title="Vender", control_type="Button").click()
sleep(3)
main.child_window(title="Nuevo", control_type="Button").click_input()
sleep(3)

#escribir nro de historia clinica, a nro 1 en el edit 
campo = main.child_window(auto_id="TxtPaciente", control_type="Edit").children(control_type="Edit")[0]
campo.set_focus()
sleep(0.3)
#cambiar a datos del .csv
campo.type_keys("1", with_spaces=True)
sleep(0.5)
send_keys("{ENTER}")

campo = main.child_window(auto_id="lueTipoPaciente", control_type="Edit")
campo.set_focus()
sleep(0.3)
#cambiar a datos del .csv
campo.type_keys("CONVENIO", with_spaces=False)
sleep(0.5)
send_keys("{ENTER}")

campo = main.child_window(auto_id="lueConvenio", control_type="Edit")
campo.set_focus()
sleep(0.3)
#cambiar a datos del .csv
campo.type_keys("COSSMIL", with_spaces=True)
sleep(0.5)
send_keys("{ENTER}")

campo = main.child_window(auto_id="lueEspecialidad", control_type="Edit")
campo.set_focus()
sleep(0.3)
#cambiar a datos del .csv
campo.type_keys("ALERGOLOGIA", with_spaces=True)
sleep(0.5)
send_keys("{ENTER}")

#agregar validacion, si es LABORATORIO, no agregar medico 
campo = main.child_window(auto_id="searchLookUpEditMedico", control_type="Edit")
campo.set_focus()
sleep(0.3)
#cambiar a datos del .csv
campo.type_keys("GUILLEN ROCHA NELVA LIZBETH", with_spaces=True)
sleep(0.5)
send_keys("{ENTER}")



grid = main.child_window(auto_id="gvListaDetalle", control_type="Table")
grid.set_focus()
sleep(0.3)

# Click en la celda de la nueva fila
celda = grid.child_window(title_re=".*Descripción row.*", control_type="Custom")
celda.click_input()
sleep(0.3)
send_keys("45100006")
sleep(0.5)
send_keys("{ENTER}")  # avanza a la siguiente celda
celda = grid.child_window(title_re=".*Medico Tratante row.*", control_type="Custom")
celda.click_input()
sleep(0.3)
send_keys("MEDICO GENERAL")
sleep(0.5)
send_keys("{ENTER}")  # avanza a la siguiente celda



main.child_window(auto_id="rdgPendiente", control_type="List").child_window(title="&Pendiente", control_type="RadioButton").click()
sleep(0.5)

main.child_window(title="Guardar", control_type="Button").click_input()
sleep(3)