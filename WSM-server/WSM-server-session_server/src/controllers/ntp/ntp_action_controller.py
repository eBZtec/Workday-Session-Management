from fastapi import HTTPException
from src.config.wsm_logger import logger
from src.services.ntp.ntp_time_service import ntpTimeService
from src.models.schema.request_models import NTP_response, LocationRequest
from timezonefinder import TimezoneFinder
from datetime import datetime
from pathlib import Path
import pytz
import json

# Global cache for loaded location data
LOCATION_DATA = None

def load_location_data():
    """
    Loads location data from the original municipios.json file provided by IBGE.
    """
    global LOCATION_DATA
    if LOCATION_DATA is None:
        try:
            file_path = Path(__file__).resolve().parent.parent.parent / "resources" / "municipios.json"
            logger.debug(f"Loading location data from file: {file_path}")
            with open(file_path, encoding="utf-8-sig") as f:
                LOCATION_DATA = json.load(f)
                logger.info(f"Location data loaded successfully. Total municipalities: {len(LOCATION_DATA)}")
        except Exception as e:
            logger.error(f"Error while loading location data: {e}")
            raise HTTPException(status_code=500, detail="Error loading location data")

# Mapping IBGE UF codes to full state names
UF_CODES = {
    11: "Rondônia", 12: "Acre", 13: "Amazonas", 14: "Roraima", 15: "Pará",
    16: "Amapá", 17: "Tocantins", 21: "Maranhão", 22: "Piauí", 23: "Ceará",
    24: "Rio Grande do Norte", 25: "Paraíba", 26: "Pernambuco", 27: "Alagoas",
    28: "Sergipe", 29: "Bahia", 31: "Minas Gerais", 32: "Espírito Santo",
    33: "Rio de Janeiro", 35: "São Paulo", 41: "Paraná", 42: "Santa Catarina",
    43: "Rio Grande do Sul", 50: "Mato Grosso do Sul", 51: "Mato Grosso",
    52: "Goiás", 53: "Distrito Federal"
}


def find_city_data_by_ibge(ibge_code: int, data: list):
    """
    Searches for a municipality using its IBGE code in the loaded data.
    """
    logger.debug(f"Searching for municipality with IBGE code: {ibge_code}")

    for municipio in data:
        if municipio["codigo_ibge"] == ibge_code:
            uf_code = municipio.get("codigo_uf")
            state_name = UF_CODES.get(uf_code, "Unknown State")
            logger.debug(f"Municipality found: {municipio}")
            return {
                "ibge_code": municipio["codigo_ibge"],
                "city": municipio["nome"],
                "state": state_name,
                "lat": municipio["latitude"],
                "lng": municipio["longitude"]
            }

    logger.warning(f"Municipality not found for IBGE code: {ibge_code}")
    return None


class NTPActionController:

    async def execute(self, location: LocationRequest):
        """
        Main method to fetch current NTP time (assumed from São Paulo timezone)
        and convert it to local time based on the IBGE municipality code.
        """
        try:
            logger.info(f"Starting NTP time process for IBGE Code: {location.ibge_code}")

            # Get NTP time from the service
            ntp_time = ntpTimeService.get_ntp_time()

            # Make NTP time timezone-aware with São Paulo timezone if it's naive
            if ntp_time.tzinfo is None:
                logger.warning("NTP time is naive. Applying timezone America/Sao_Paulo manually.")
                sao_paulo_tz = pytz.timezone("America/Sao_Paulo")
                ntp_time = sao_paulo_tz.localize(ntp_time)

            logger.debug(f"NTP time set to Sao Paulo timezone: {ntp_time}")

            # Load location data (once)
            load_location_data()

            # Find municipality info by IBGE code
            city_data = find_city_data_by_ibge(location.ibge_code, LOCATION_DATA)
            if not city_data:
                logger.error(f"Municipality not found for IBGE code: {location.ibge_code}")
                raise HTTPException(status_code=404, detail="Location not found")

            # Determine timezone using latitude/longitude
            tf = TimezoneFinder()
            timezone_str = tf.timezone_at(lat=city_data["lat"], lng=city_data["lng"])
            logger.info(f"Timezone found for {city_data['city']}: {timezone_str}")

            if not timezone_str:
                logger.error(f"Timezone not found for coordinates: {city_data}")
                raise HTTPException(status_code=404, detail="Timezone not found")

            # Convert NTP time (São Paulo) to local time
            city_tz = pytz.timezone(timezone_str)
            local_time = datetime.now(city_tz)
            logger.debug(f"Local time converted: {local_time}")

            return NTP_response(
                ntp=ntp_time.strftime('%Y-%m-%d %H:%M:%S'),
                local_time=local_time.strftime('%Y-%m-%d %H:%M:%S'),
                country="Brazil",
                state=city_data["state"],
                city=city_data["city"]
            )

        except HTTPException as http_exc:
            logger.warning(f"HTTPException caught: {http_exc.detail}")
            raise http_exc

        except Exception as e:
            logger.exception("Unexpected error while processing NTP location request.")
            raise HTTPException(status_code=500, detail="Unexpected error occurred")