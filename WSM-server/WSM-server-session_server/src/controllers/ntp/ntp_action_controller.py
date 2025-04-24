from fastapi import HTTPException
from src.config.wsm_logger import logger
from src.services.ntp.ntp_time_service import ntpTimeService
from src.models.schema.request_models import NTP_response, LocationRequest
from timezonefinder import TimezoneFinder
from datetime import datetime, timedelta
import pytz
import json
from pathlib import Path

LOCATION_DATA = None

def load_location_data():
    global LOCATION_DATA
    if LOCATION_DATA is None:
        try:
            file_path = Path(__file__).resolve().parent.parent.parent / "resources" / "countries+states+cities.json"
            logger.debug(f"Carregando dados de localização do arquivo: {file_path}")
            with open(file_path, encoding="utf-8") as f:
                LOCATION_DATA = json.load(f)
                logger.info("Dados de localização carregados com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao carregar dados de localização: {e}")
            raise HTTPException(status_code=500, detail="Erro ao carregar dados de localização")

def find_city_data(country: str, state: str, city: str, data: list):
    logger.debug(f"Buscando cidade: País={country}, Estado={state}, Cidade={city}")
    country = country.strip().lower()
    state = state.strip().lower()
    city = city.strip().lower()

    for country_entry in data:
        if country_entry["name"].strip().lower() == country:
            for state_entry in country_entry.get("states", []):
                if state_entry["name"].strip().lower() == state:
                    for city_entry in state_entry.get("cities", []):
                        if city_entry["name"].strip().lower() == city:
                            logger.debug(f"Cidade encontrada: {city_entry}")
                            return {
                                "lat": float(city_entry["latitude"]),
                                "lng": float(city_entry["longitude"]),
                                "city": city_entry["name"],
                                "state": state_entry["name"],
                                "country": country_entry["name"]
                            }
    logger.warning(f"Localização não encontrada: {country}, {state}, {city}")
    return None


class NTPActionController:

    async def execute(self, location: LocationRequest):
        try:
            logger.info(f"Iniciando execução com local: {location}")
            ntp_time = ntpTimeService.get_ntp_time()
            logger.debug(f"NTP time recebido: {ntp_time}")

            if ntp_time is None:
                logger.error("Falha ao obter o horário NTP.")
                raise HTTPException(status_code=500, detail="Could not retrieve NTP time")

            load_location_data()
            city_data = find_city_data(location.country, location.state, location.city, LOCATION_DATA)

            if not city_data:
                logger.error(f"Dados da cidade não encontrados para: {location}")
                raise HTTPException(status_code=404, detail="Location not found")

            tf = TimezoneFinder()
            timezone_str = tf.timezone_at(lat=city_data["lat"], lng=city_data["lng"])
            logger.info(f"Timezone encontrado para localização {city_data['city']}: {timezone_str}")

            if not timezone_str:
                logger.error(f"Timezone não encontrado para coordenadas: {city_data}")
                raise HTTPException(status_code=404, detail="Timezone not found")

            local_time = ntp_time.astimezone(pytz.timezone(timezone_str))
            logger.debug(f"Horário local convertido: {local_time}")

            return NTP_response(
                ntp=ntp_time.strftime('%Y-%m-%d %H:%M:%S %Z%z'),
                local_time=local_time.strftime('%Y-%m-%d %H:%M:%S %Z%z'),
                country=city_data["country"],
                state=city_data["state"],
                city=city_data["city"]
            )

        except HTTPException as http_exc:
            logger.warning(f"HTTPException capturada: {http_exc.detail}")
            raise http_exc
        except Exception as e:
            logger.exception("Erro inesperado ao processar requisição de localização.")
            raise HTTPException(status_code=500, detail="Unexpected error occurred")
