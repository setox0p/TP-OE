import datetime
import re

# 1: BDD Simulada
bd_empleados = {
    "EMP-101": {"nombre": "Juan Pérez", "dias_disponibles": 14},
    "EMP-102": {"nombre": "María Gómez", "dias_disponibles": 7},
    "EMP-103": {"nombre": "Carlos López", "dias_disponibles": 21}
}
bd_solicitudes = []

# 2: Cfg de la máquina de estado

ESTADO_INICIO = "INICIO"
ESTADO_VALIDAR_LEGAJO = "VALIDAR_LEGAJO"
ESTADO_FECHA_INICIO = "FECHA_INICIO"
ESTADO_FECHA_FIN = "FECHA_FIN"
ESTADO_PROCESAR = "PROCESAR"

class BotVacacionesSimulador:
    def __init__(self):
        self.estado_actual = ESTADO_INICIO
        self.datos_sesion = {}

    def validar_fecha(self, fecha_texto):
        # Validación de robustez mediante expresiones regulares (Formato YYYY-MM-DD)
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", fecha_texto):
            return False
        try:
            datetime.datetime.strptime(fecha_texto, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def procesar_mensaje(self, mensaje):
        mensaje = mensaje.strip()
        
        if mensaje.lower() == '/start' or self.estado_actual == ESTADO_INICIO:
            self.estado_actual = ESTADO_VALIDAR_LEGAJO
            self.datos_sesion = {}
            return "🤖 [BOT]: ¡Hola! Bienvenido al asistente de Gestión de Vacaciones.\nPor favor, ingrese su número de legajo (Ej: EMP-101):"

        # --- ESTADO 1: VALIDACIÓN DE LEGAJO (COMPUERTA LÓGICA 1) ---
        if self.estado_actual == ESTADO_VALIDAR_LEGAJO:
            if mensaje in bd_empleados:
                self.datos_sesion["legajo"] = mensaje
                self.datos_sesion["nombre"] = bd_empleados[mensaje]["nombre"]
                self.estado_actual = ESTADO_FECHA_INICIO
                return f"✅ [BOT]: Empleado verificado: {self.datos_sesion['nombre']}.\n🗓️ Ingrese la fecha de INICIO de sus vacaciones (Formato: AAAA-MM-DD):"
            else:
                # Camino Infeliz: Legajo incorrecto
                return "❌ [BOT]: El legajo ingresado no existe. Inténtelo de nuevo o comuníquese con RR.HH.:"

        # --- ESTADO 2: CAPTURA FECHA INICIO (CAMINO INFELIZ PROCESADO) ---
        if self.estado_actual == ESTADO_FECHA_INICIO:
            if self.validar_fecha(mensaje):
                self.datos_sesion["fecha_inicio"] = datetime.datetime.strptime(mensaje, "%Y-%m-%d")
                self.estado_actual = ESTADO_FECHA_FIN
                return "🗓️ [BOT]: Excelente. Ahora ingrese la fecha de FINALIZACIÓN (Formato: AAAA-MM-DD):"
            else:
                return "⚠️ [BOT]: Formato inválido o fecha inexistente. Por favor use el formato estricto AAAA-MM-DD (Ej: 2026-01-15):"

        # --- ESTADO 3: CAPTURA FECHA FIN Y VALIDACIÓN DE NEGOCIO (COMPUERTA LÓGICA 2) ---
        if self.estado_actual == ESTADO_FECHA_FIN:
            if not self.validar_fecha(mensaje):
                return "⚠️ [BOT]: Formato inválido. Por favor ingrese la fecha de FINALIZACIÓN en formato AAAA-MM-DD:"
            
            fecha_fin_dt = datetime.datetime.strptime(mensaje, "%Y-%m-%d")
            if fecha_fin_dt <= self.datos_sesion["fecha_inicio"]:
                return "⚠️ [BOT]: La fecha de finalización debe ser posterior a la fecha de inicio. Ingrese otra fecha:"

            self.datos_sesion["fecha_fin"] = fecha_fin_dt
            
            # Calcular días solicitados
            dias_solicitados = (self.datos_sesion["fecha_fin"] - self.datos_sesion["fecha_inicio"]).days + 1
            legajo = self.datos_sesion["legajo"]
            dias_disponibles = bd_empleados[legajo]["dias_disponibles"]

            # Evaluación de reglas de negocio dinámicas
            if dias_solicitados <= dias_disponibles:
                # Camino Feliz: Registro Exitoso
                bd_empleados[legajo]["dias_disponibles"] -= dias_solicitados
                solicitud_id = len(bd_solicitudes) + 1
                bd_solicitudes.append({
                    "id": solicitud_id, "legajo": legajo, 
                    "inicio": self.datos_sesion["fecha_inicio"].strftime("%Y-%m-%d"),
                    "fin": self.datos_sesion["fecha_fin"].strftime("%Y-%m-%d"), "estado": "APROBADO"
                })
                self.estado_actual = ESTADO_INICIO
                return (f"🎉 [BOT]: ¡SOLICITUD APROBADA AUTOMÁTICAMENTE!\n"
                        f"📊 Detalle:\n"
                        f"- Días solicitados: {dias_solicitados}\n"
                        f"- Nuevos días disponibles en BD: {bd_empleados[legajo]['dias_disponibles']}\n"
                        f"La solicitud ha sido guardada con el ID #{solicitud_id}. ¡Buen descanso!\n\n"
                        f"Escriba /start si desea realizar otra consulta.")
            else:
                # Camino Infeliz: Rechazo por falta de saldo
                self.estado_actual = ESTADO_INICIO
                return (f"❌ [BOT]: SOLICITUD RECHAZADA.\n"
                        f"Usted solicitó {dias_solicitados} días, pero solo dispone de {dias_disponibles} días.\n"
                        f"Proceso finalizado. Escriba /start para reiniciar.")


# Simulación de la ejecución en consola
if __name__ == "__main__":
    bot = BotVacacionesSimulador()
    print("--- INICIANDO CONSOLA DE SIMULACIÓN DEL CHATBOT ---")
    print("Escriba '/start' para iniciar el flujo.")
    while True:
        entrada = input("Usuario: ")
        if entrada.lower() == 'salir':
            break
        respuesta = bot.procesar_mensaje(entrada)
        print(respuesta)