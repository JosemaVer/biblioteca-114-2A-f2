"""
Módulo de Consumo de API Externa: mindicador.cl
Obtiene el valor observado del dólar con tiempo máximo de espera (timeout) y mecanismo de tolerancia a fallos.
"""
import requests


# Valor de respaldo predeterminado para el 5 de octubre de 2026 en caso de no disponer de internet
DOLAR_FALLBACK_DEFAULT = 984.82


def obtener_valor_dolar(timeout: int = 5, valor_respaldo: float = DOLAR_FALLBACK_DEFAULT) -> tuple[float, str]:
    """
    Consulta la API pública de mindicador.cl para obtener el valor del dólar en CLP.
    
    Parámetros:
        timeout (int): Tiempo máximo de espera en segundos para la respuesta del servidor.
        valor_respaldo (float): Valor a utilizar si la API no está disponible o falla la red.
        
    Retorna:
        tuple[float, str]: (valor_dolar, origen_dato)
            - valor_dolar: El valor numérico del dólar en pesos chilenos.
            - origen_dato: Cadena explicativa ("API mindicador.cl" o "Respaldo local (Sin conexión)").
    """
    url = "https://mindicador.cl/api/dolar"
    
    try:
        # Petición HTTP GET con timeout de seguridad
        respuesta = requests.get(url, timeout=timeout)
        
        # Validamos código de respuesta HTTP (200 OK)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            # mindicador.cl devuelve la serie con el valor más reciente en la posición 0
            if "serie" in datos and len(datos["serie"]) > 0:
                valor = float(datos["serie"][0]["valor"])
                return valor, "API mindicador.cl (En vivo)"
            elif "dolar" in datos and "valor" in datos["dolar"]:
                valor = float(datos["dolar"]["valor"])
                return valor, "API mindicador.cl (En vivo)"
                
        # Si la API respondió con error no 200
        print(f"\n[Aviso API]: El servidor respondió con estado {respuesta.status_code}. Usando valor de respaldo.")
        return valor_respaldo, f"Respaldo local (${valor_respaldo:,.2f} CLP)"

    except requests.exceptions.Timeout:
        print(f"\n[Aviso de Red]: Tiempo de espera agotado ({timeout}s) al contactar mindicador.cl.")
        print(f"   [INFO] Se utilizará el valor de contingencia configurado: ${valor_respaldo:,.2f} CLP.")
        return valor_respaldo, f"Respaldo local (${valor_respaldo:,.2f} CLP - Timeout)"

    except requests.exceptions.RequestException as error_red:
        print(f"\n[Aviso de Conexión]: No fue posible conectar con el servicio externo ({error_red.__class__.__name__}).")
        print(f"   [INFO] El sistema continuará operando normalmente con el valor de respaldo: ${valor_respaldo:,.2f} CLP.")
        return valor_respaldo, f"Respaldo local (${valor_respaldo:,.2f} CLP - Sin conexión)"

    except Exception as error_inesperado:
        print(f"\n[Aviso General]: Error inesperado al procesar la API ({error_inesperado}).")
        return valor_respaldo, f"Respaldo local (${valor_respaldo:,.2f} CLP)"
