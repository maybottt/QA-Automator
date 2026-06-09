import os
import csv
from pywinauto.application import Application
from pywinauto.keyboard import send_keys
from time import sleep
from pywinauto import Desktop

# Definimos las rutas
path_app = r'C:\Program Files (x86)\SEDNA SRL\GeCOIN plus ERP\WinVentas.exe'
dir_app = os.path.dirname(path_app) # Extrae la carpeta contenedora

# Conectamos a la aplicación si ya está abierta o la iniciamos de cero
app = None
main = None

print("Buscando si la ventana principal 'Ventas' ya está activa...")
try:
    # Si ya está abierta la ventana de Ventas, la conectamos directamente
    app = Application(backend="uia").connect(title_re=".*Ventas.*")
    main = Desktop(backend="uia").window(auto_id="mainVentas")
    if main.exists(timeout=2):
        print("Aplicación ya iniciada en la pantalla principal. Saltando login.")
except Exception:
    print("La pantalla principal no está activa. Intentaremos conectar o iniciar el login...")

# Si no está en la pantalla principal, manejamos el flujo de inicio/login
if main is None or not main.exists():
    try:
        # Intentamos conectar a una instancia de login activa
        app = Application(backend="uia").connect(title_re=".*Login.*")
        print("Conectado a ventana de login abierta.")
    except Exception:
        # Si no hay nada abierto, iniciamos el ejecutable
        print("Iniciando la aplicación desde cero con pywinauto...")
        app = Application(backend="uia").start(path_app, work_dir=dir_app)
        sleep(2.5)

    # Buscar la ventana de login
    dialog = None
    try:
        dialog = app.frmLogin2
        dialog.wait('visible', timeout=5)
    except Exception:
        try:
            dialog = Desktop(backend='uia').frmLogin2
            dialog.wait('visible', timeout=5)
        except Exception:
            print("No se pudo detectar la ventana de login.")

    if dialog and dialog.exists():
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
        sleep(8)

# Aseguramos que la ventana Ventas esté lista
main = Desktop(backend="uia").window(auto_id="mainVentas")
main.wait("exists enabled visible", timeout=20)
print("Ventana Ventas encontrada")

# Hacemos clic en "Vender" solo si el botón está disponible (si ya estamos dentro, omitimos)
try:
    btn_vender = main.child_window(title="Vender", control_type="Button")
    if btn_vender.exists(timeout=2) and btn_vender.is_visible():
        btn_vender.click()
        sleep(3)
except Exception:
    print("Ya se encuentra en la pantalla de ventas o el botón 'Vender' no está activo.")

# Ruta del archivo CSV
csv_path = os.path.join(os.path.dirname(__file__), 'datos_ventas.csv')

if not os.path.exists(csv_path):
    print(f"Error: El archivo CSV no existe en la ruta: {csv_path}")
else:
    print(f"Leyendo casos de prueba desde: {csv_path}")
    
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            is_first_doctor_entry = True
            print(f"\n--- Iniciando Venta #{i} (Paciente: {row['paciente']}) ---")
            
            # Click en Nuevo para limpiar/iniciar una nueva transacción
            main.child_window(title="Nuevo", control_type="Button").click_input()
            sleep(3)
            
            # 1. Historia Clínica (Paciente)
            campo = main.child_window(auto_id="TxtPaciente", control_type="Edit").children(control_type="Edit")[0]
            campo.set_focus()
            sleep(0.3)
            campo.type_keys(row['paciente'], with_spaces=True)
            sleep(0.5)
            send_keys("{ENTER}")
            sleep(1) # Esperamos a que se carguen los datos del paciente en el ERP
            
            # 2. Tipo Paciente
            campo = main.child_window(auto_id="lueTipoPaciente", control_type="Edit")
            campo.set_focus()
            sleep(0.3)
            campo.type_keys(row['tipo_paciente'], with_spaces=False)
            sleep(0.5)
            send_keys("{ENTER}")
            sleep(0.5)

            # VALIDACIÓN: si es CONVENIO, elige tipo de convenio
            if row['tipo_paciente'].strip().upper() == "CONVENIO":
                print(f"Tipo paciente: CONVENIO. Rellenando convenio: {row['convenio']}")
                campo = main.child_window(auto_id="lueConvenio", control_type="Edit")
                campo.set_focus()
                sleep(0.3)
                campo.type_keys(row['convenio'], with_spaces=True)
                sleep(0.5)
                send_keys("{DOWN}")
                send_keys("{ENTER}")
                sleep(0.5)
            else:
                print(f"Tipo paciente: {row['tipo_paciente']}. Se omite la selección de convenio.")

            # 3. Especialidad
            campo = main.child_window(auto_id="lueEspecialidad", control_type="Edit")
            campo.set_focus()
            sleep(0.3)
            campo.type_keys(row['especialidad'], with_spaces=True)
            sleep(0.5)
            send_keys("{ENTER}")
            sleep(0.5)

            # VALIDACIÓN: si es LABORATORIO, no agregar médico
            if row['especialidad'].strip().upper() != "LABORATORIO":
                print(f"Especialidad: {row['especialidad']}. Rellenando médico: {row['medico']}")
                campo = main.child_window(auto_id="searchLookUpEditMedico", control_type="Edit")
                campo.set_focus()
                sleep(0.3)
                campo.type_keys(row['medico'], with_spaces=True)
                sleep(0.5)
                send_keys("{ENTER}")
                sleep(0.5)
            else:
                print("Especialidad es LABORATORIO. Se omite la asignación de médico.")

            # 4. Detalle de los artículos en la Grilla
            grid = main.child_window(auto_id="gvListaDetalle", control_type="Table")
            grid.set_focus()
            sleep(1.0) # Damos un poco más de tiempo para asegurar el renderizado de la grilla

            # Click en la celda de la nueva fila (Item o Descripción)
            try:
                # Intentamos primero en 'Item row' (ya que el código del artículo se introduce en esa columna)
                try:
                    celda = grid.child_window(title_re=".*Item row.*", control_type="DataItem")
                    celda.wait('exists visible enabled', timeout=3)
                    celda.click_input()
                except Exception:
                    # Fallback a 'Descripción row'
                    celda = grid.child_window(title_re=".*Descripción row.*", control_type="DataItem")
                    celda.wait('exists visible enabled', timeout=3)
                    celda.click_input()
            except Exception as e:
                print("\n[DEBUG ERROR] No se encontró la celda 'Item' o 'Descripción' en la grilla.")
                print("Imprimiendo los identificadores de control de la grilla para depurar:")
                try:
                    grid.print_control_identifiers()
                except Exception as ex:
                    print("No se pudo imprimir los controles de la grilla:", ex)
                raise e
            sleep(0.3)
            send_keys(row['codigo_articulo'])
            sleep(0.5)
            send_keys("{ENTER}")  # Avanza a la siguiente celda (normalmente Cantidad o similar)
            sleep(0.5)

            # Click en la celda del Médico Tratante
            celda = grid.child_window(title_re=".*Medico Tratante row.*", control_type="DataItem")
            celda.click_input()
            sleep(0.3)

            if is_first_doctor_entry:
                print("Primera entrada de médico. Enviando TAB para abrir diálogo de búsqueda...")
                send_keys("{TAB}")
                sleep(1.0) # Esperamos a que abra la ventana Listas (frmMedicos)

                try:
                    # Detectar la ventana emergente frmMedicos
                    popup_medicos = main.child_window(auto_id="frmMedicos", control_type="Window")
                    popup_medicos.wait('exists visible', timeout=4)
                    print("Ventana de búsqueda 'Listas' (frmMedicos) abierta.")

                    # Escribimos el nombre del médico en la barra de búsqueda (está enfocada por defecto)
                    send_keys(row['medico_tratante'], with_spaces=True)
                    sleep(0.5)
                    send_keys("{ENTER}") # Presionar Enter para buscar/filtrar
                    sleep(0.8)

                    # Seleccionamos la celda con el nombre en la tabla del popup
                    grid_popup = popup_medicos.child_window(auto_id="gridControl1", control_type="Table")
                    celda_medico = grid_popup.child_window(title_re=".*Nombres row.*")
                    # celda_medico.click_input()
                    send_keys("{DOWN}")
                    sleep(0.3)
                    send_keys("{ENTER}") # Confirma y cierra la ventana
                    sleep(1.0)
                    
                    is_first_doctor_entry = False # Siguientes filas se autocompletarán
                except Exception as e:
                    print("Error interactuando con la ventana emergente de médicos:", e)
                    send_keys("{ENTER}")
                    sleep(0.5)
            else:
                print("Entrada subsecuente. Se asume autocompletado en la celda.")
                # Presionamos ENTER en la grilla para confirmar la edición de la fila actual
                send_keys("{ENTER}")
                sleep(0.5)
            # Ingreso del segundo artículo (opcional, si existe en el CSV)
            if 'codigo_articulo2' in row and row['codigo_articulo2'].strip():
                print(f"Ingresando segundo artículo: {row['codigo_articulo2']}")
                
                # Click en la celda de la nueva fila (Item o Descripción)
                try:
                    try:
                        celda = grid.child_window(title_re=".*Item row.*", control_type="DataItem")
                        celda.wait('exists visible enabled', timeout=3)
                        celda.click_input()
                    except Exception:
                        celda = grid.child_window(title_re=".*Descripción row.*", control_type="DataItem")
                        celda.wait('exists visible enabled', timeout=3)
                        celda.click_input()
                except Exception as e:
                    print("No se pudo encontrar la celda del segundo artículo:", e)
                
                sleep(0.3)
                send_keys(row['codigo_articulo2'])
                sleep(0.5)
                send_keys("{ENTER}")
                send_keys("{ENTER}")
                send_keys("{ENTER}")
                send_keys("{ENTER}") # Avanza a la siguiente celda
                sleep(0.5)

                # Confirmamos el médico tratante del segundo artículo (se autocompleta)
                try:
                    celda = grid.child_window(title_re=".*Medico Tratante row.*", control_type="DataItem")
                    celda.click_input()
                    sleep(0.3)
                    send_keys("{ENTER}") # Confirma y registra la segunda fila
                    sleep(0.5)
                except Exception as e:
                    print("No se pudo confirmar el médico tratante del segundo artículo:", e)

            # 5. Marcar como Pendiente
            main.child_window(auto_id="rdgPendiente", control_type="List").child_window(title="&Pendiente", control_type="RadioButton").click()
            sleep(0.5)

            # 6. Guardar la venta
            main.child_window(title="Guardar", control_type="Button").click_input()
            sleep(2) # Esperar a que guarde y aparezca el popup

            # 7. Manejo robusto de popup de confirmación tras Guardar
            try:
                popup_ficha = main.child_window(auto_id="frmPreview", control_type="Window")
                popup_ficha.wait('exists visible', timeout=4)
                print('Se detecto frmPreview')
                popup_ficha.child_window(title="Salir", control_type="Button").click()
                
                # Presiona ENTER para RECHAZAR Registrar para el mismo paciente? 
                send_keys("{TAB}") 
                send_keys("{ENTER}") 
                sleep(1)
            except Exception as e:
                print("No se detectó ningún popup de confirmación emergente o se cerró automáticamente.")
            