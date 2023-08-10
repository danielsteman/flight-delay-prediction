from extract import FlightDataManager, FlightsClient
from storage_manager import StorageManager

manager = FlightDataManager(FlightsClient(), StorageManager("flight-delay-prediction"))
manager.get_all_flights()
manager.upload_all()
