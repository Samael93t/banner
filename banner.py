import os
import subprocess
import shlex

# Constantes para rutas y nombres de archivos
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".banner_config")
BASHRC_FILE = os.path.join(os.path.expanduser("~"), ".bashrc")
SCRIPT_PATH = os.path.abspath(__file__)

def instalar_paquete(paquete):
    """Instala un paquete usando pkg si no está instalado."""
    try:
        subprocess.run([paquete, "--version"], check=True, capture_output=True)
        print(f"{paquete} ya está instalado.")
    except (FileNotFoundError, subprocess.CalledProcessError):
        print(f"Instalando {paquete}...")
        try:
            subprocess.run(["pkg", "install", paquete, "-y"], check=True)
            print(f"{paquete} instalado con éxito.")
        except subprocess.CalledProcessError as e:
            print(f"Error al instalar {paquete}: {e}")
            exit(1)

def instalar_lolcat():
    """Instala lolcat usando gem."""
    try:
        subprocess.run(["lolcat", "--version"], check=True, capture_output=True)
        print("lolcat ya está instalado.")
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("Instalando lolcat usando gem...")
        try:
            # Primero, asegúrate de que ruby esté instalado
            subprocess.run(["pkg", "install", "ruby", "-y"], check=True)
            # Luego, instala lolcat usando gem
            subprocess.run(["gem", "install", "lolcat"], check=True, capture_output=True)
            print("lolcat instalado con éxito usando gem.")
        except subprocess.CalledProcessError as e:
            print(f"Error al instalar lolcat usando gem: {e}")
            exit(1)

def guardar_configuracion(texto, ruta_cancion):
    """Guarda la configuración en el archivo de configuración."""
    try:
        with open(CONFIG_FILE, "w") as f:
            f.write(f"texto={texto}\n")
            f.write(f"ruta_cancion={ruta_cancion}\n")
        print("Configuración guardada con éxito.")
    except IOError as e:
        print(f"Error al guardar la configuración: {e}")

def cargar_configuracion():
    """Carga la configuración desde el archivo de configuración."""
    try:
        with open(CONFIG_FILE, "r") as f:
            configuracion = {}
            for linea in f:
                clave, valor = linea.strip().split("=", 1)
                configuracion[clave] = valor
            return configuracion
    except FileNotFoundError:
        return None
    except IOError as e:
        print(f"Error al leer la configuración: {e}")
        return None
    except ValueError:
        print("Error: El archivo de configuración está corrupto.")
        return None

def agregar_a_bashrc():
    """Añade la ejecución del script al final de .bashrc si no existe."""
    try:
        with open(BASHRC_FILE, "r+") as f:
            lines = f.readlines()
            script_line = f"python {SCRIPT_PATH}"
            if not any(line.strip() == script_line for line in lines):
                f.write(f"\n{script_line}\n")
                print("Script añadido a .bashrc. Reinicia Termux para aplicar los cambios.")
            else:
                print("El script ya está en .bashrc.")
    except IOError as e:
        print(f"Error al modificar .bashrc: {e}")

def borrar_configuracion():
    """Borra el archivo de configuración."""
    try:
        os.remove(CONFIG_FILE)
        print("Configuración borrada con éxito.")
    except FileNotFoundError:
        print("No existe una configuración guardada.")
    except OSError as e:
        print(f"Error al borrar la configuración: {e}")

def modificar_configuracion():
    """Permite al usuario modificar la configuración existente."""
    configuracion = cargar_configuracion()
    if configuracion:
        texto_actual = configuracion.get("texto", "")
        ruta_cancion_actual = configuracion.get("ruta_cancion", "")

        texto = input(f"Ingrese el nuevo texto para el banner ({texto_actual}): ") or texto_actual
        ruta_cancion = input(f"Ingrese la nueva ruta de la canción ({ruta_cancion_actual}): ") or ruta_cancion_actual

        guardar_configuracion(texto, ruta_cancion)
        print("Configuración modificada con éxito.")
    else:
        print("No existe una configuración guardada.")

def crear_banner():
    """Crea y muestra el banner."""
    instalar_paquete("mpv")
    instalar_paquete("figlet")
    instalar_lolcat()  # Usar la función de instalación de lolcat con gem

    configuracion = cargar_configuracion()
    if configuracion:
        texto = configuracion["texto"]
        ruta_cancion = configuracion["ruta_cancion"]
    else:
        texto = input("Ingrese el texto para el banner: ")
        ruta_cancion = input("Ingrese la ruta de la canción: ")
        guardar_configuracion(texto, ruta_cancion)
        agregar_a_bashrc()
        print("¡Listo! El banner se mostrará cada vez que abras Termux.")

    os.system("clear")
    try:
        # Ejecutar figlet y lolcat usando subprocess.Popen para la tubería
        figlet_process = subprocess.Popen(["figlet", "-f", "standard", texto], stdout=subprocess.PIPE)
        lolcat_process = subprocess.Popen(["lolcat", "-F", "0.5"], stdin=figlet_process.stdout, stdout=subprocess.PIPE)
        figlet_process.stdout.close()  # Permitir que figlet termine
        output, error = lolcat_process.communicate()

        if error:
            print(f"Error al ejecutar lolcat: {error.decode()}")
        else:
            print(output.decode())

    except FileNotFoundError:
        print("Error: figlet o lolcat no se encontraron. Asegúrate de que están instalados.")
        return

    try:
        subprocess.run(["mpv", "--start=0", "--length=30", ruta_cancion], check=True)
    except FileNotFoundError:
        print("Error: mpv no se encontró. Asegúrate de que está instalado.")
    except subprocess.CalledProcessError:
        print("Error: No se pudo reproducir la canción. Verifica la ruta del archivo.")

def main():
    """Función principal que maneja el menú y la lógica del script."""
    configuracion = cargar_configuracion()
    while True:
        if configuracion:
            print("\nOpciones:")
            print("1. Mostrar banner")
            print("2. Borrar configuración")
            print("3. Modificar configuración")
            print("4. Salir")
            opcion = input("Ingrese su opción: ")

            if opcion == "1":
                crear_banner()
            elif opcion == "2":
                borrar_configuracion()
                configuracion = None
            elif opcion == "3":
                modificar_configuracion()
                configuracion = cargar_configuracion()
            elif opcion == "4":
                print("Saliendo...")
                break
            else:
                print("Opción inválida. Intente de nuevo.")
        else:
            crear_banner()
            configuracion = cargar_configuracion()

if __name__ == "__main__":
    main()
    main()
