import json
import os
from typing import Any, Dict

import requests
from dotenv import load_dotenv


def crear_usuario(
    mrbot_user: str,
    base_url: str,
    user_endpoint: str,
) -> Dict[str, Any]:
    """
    Crea un nuevo usuario en la API y retorna el JSON de respuesta.

    Args:
        mrbot_user (str): Email del futuro usuario.
        base_url (str): URL base de Mrbot (p.ej. https://api-bots.mrbot.com.ar).
        user_endpoint (str): Endpoint de usuario (p.ej. api/v1/user).

    Returns:
        Dict[str, Any]: JSON retornado por la API con los datos del usuario creado.
    """
    url = f"{base_url.rstrip('/')}/{user_endpoint.lstrip('/')}"

    payload = json.dumps({"mail": mrbot_user})
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    response = requests.post(url, headers=headers, data=payload)
    try:
        parsed = response.json()
    except ValueError:
        response.raise_for_status()
        raise

    print(response.text)
    return parsed


def resetear_api_key(
    mrbot_user: str,
    base_url: str,
    user_endpoint: str,
) -> Dict[str, Any]:
    """
    Resetea la API Key del usuario y retorna el JSON con la nueva clave.

    Args:
        mrbot_user (str): Email del usuario existente.
        base_url (str): URL base de Mrbot.
        user_endpoint (str): Endpoint de usuario.

    Returns:
        Dict[str, Any]: JSON retornado por la API con mensaje y nueva API key.
    """
    url = f"{base_url.rstrip('/')}/{user_endpoint.lstrip('/')}/reset-key/"

    # Según OpenAPI, email va como query parameter
    params = {"email": mrbot_user}
    headers = {
        "Accept": "application/json",
    }

    response = requests.post(url, headers=headers, params=params)
    try:
        parsed = response.json()
    except ValueError:
        response.raise_for_status()
        raise

    print(response.text)
    return parsed


def obtener_consultas_disponibles(
    mrbot_user: str,
    mrbot_api_key: str,
    base_url: str,
    user_endpoint: str,
) -> Dict[str, Any]:
    """
    Obtiene el estado/uso de consultas disponibles para el usuario.

    Args:
        mrbot_user (str): Email del usuario.
        mrbot_api_key (str): API key asociada al usuario.
        base_url (str): URL base de Mrbot.
        user_endpoint (str): Endpoint de usuario.

    Returns:
        Dict[str, Any]: JSON retornado por la API con las consultas disponibles.
    """
    # Según OpenAPI, email va en el path
    url = f"{base_url.rstrip('/')}/{user_endpoint.lstrip('/')}/consultas/{mrbot_user}"

    headers = {
        "x-api-key": mrbot_api_key,
        "Accept": "application/json",
    }

    response = requests.get(url, headers=headers)
    try:
        parsed = response.json()
    except ValueError:
        response.raise_for_status()
        raise

    print(response.text)
    return parsed


def main() -> None:
    load_dotenv()

    mrbot_user = os.getenv("MAIL") or os.getenv("MAIL")
    mrbot_api_key = os.getenv("MRBOT_API_KEY")
    base_url = os.getenv("BASE_URL", "https://api-bots.mrbot.com.ar")
    user_endpoint = os.getenv("USER_ENDPOINT", "api/v1/user")

    assert base_url and user_endpoint and mrbot_user, "Faltan credenciales obligatorias"

    # Crear usuario (comentar si ya existe)
    if os.getenv("EJECUTAR_CREAR_USUARIO", "false").lower() == "true":
        try:
            response = crear_usuario(
                mrbot_user=mrbot_user,
                base_url=base_url,
                user_endpoint=user_endpoint,
            )
            print(f"Usuario creado: {response.get('message')}")
        except Exception as exc:
            print(f"Error creando usuario: {exc}")

    # Resetear API Key
    try:
        response = resetear_api_key(
            mrbot_user=mrbot_user,
            base_url=base_url,
            user_endpoint=user_endpoint,
        )
        # Intentar extraer la nueva API key de la respuesta
        if isinstance(response.get("data"), dict):
            nueva_api_key = response["data"].get("api_key")
            if nueva_api_key:
                print(f"Nueva API Key obtenida: {nueva_api_key}")
                mrbot_api_key = nueva_api_key
    except RuntimeError as exc:
        print(str(exc))
        return
    except Exception as exc:
        print(f"Error reseteando API Key: {exc}")
        return

    # Obtener consultas disponibles
    if mrbot_api_key:
        try:
            response = obtener_consultas_disponibles(
                mrbot_user=mrbot_user,
                mrbot_api_key=mrbot_api_key,
                base_url=base_url,
                user_endpoint=user_endpoint,
            )
            print("Consultas disponibles obtenidas correctamente.")
        except RuntimeError as exc:
            print(str(exc))
        except Exception as exc:
            print(f"Error obteniendo consultas disponibles: {exc}")
    else:
        print("No se pudo obtener API Key, saltando consulta de disponibles.")


if __name__ == "__main__":
    main()
