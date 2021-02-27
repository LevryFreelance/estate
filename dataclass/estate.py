from dataclasses import dataclass


@dataclass
class Estate:
    year: int = None
    month: int = None
    day: int = None
    country: str = None
    resource: str = None
    deal_type: str = None
    property_type: str = None
    region: str = None
    city: str = None
    district: str = None
    address: str = None
    price: int = None
    price_m2: int = None
    area: int = None
    ground_area: int = None
    room_number: int = None
    floor_number: int = None
    count_of_floors: int = None
    kad_number: str = None
    series: str = None
    house_type: str = None
    facilities: str = None
    purpose: str = None
    link: str = None


    def to_list(self):
        return {"year": self.year, "month": self.month, "day": self.day, "country": self.country, "resource": self.resource, "deal_type": self.deal_type, "property_type": self.property_type, "region": self.region, "city": self.city, "district": self.district, "address": self.address,
                "price": self.price, "price_m2": self.price_m2, "area": self.area, "ground_area": self.ground_area,
                "room_number": self.room_number, "floor_number": self.floor_number, "count_of_floors": self.count_of_floors, "kad_number": self.kad_number, "series": self.series,
                "house_type": self.house_type, "facilities": self.facilities, "purpose": self.purpose, "link": self.link}
