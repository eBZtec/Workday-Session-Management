from src.logs.logger import WSMLogger
"""
Singleton criado para evitar importação circular entre o config.py e o logger.py
"""
logger = WSMLogger()