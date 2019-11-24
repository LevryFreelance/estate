from dataclasses import dataclass


@dataclass
class Estate:
    parsing_date: str = None
    year: int = None
    month: int = None
    country: str = None
    resource: str = None
    deal_type: str = None
    property_type: str = None
    city_region: str = None
    district: str = None
    street: str = None
    volost: str = None
    village: str = None
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
        return {"parsing_date": self.parsing_date, "year": self.year, "month": self.month, "country": self.country, "resource": self.resource, "deal_type": self.deal_type, "property_type": self.property_type, "city_region": self.city_region, "district": self.district,
                "street": self.street, "volost": self.volost, "village": self.village, "price": self.price, "price_m2": self.price_m2, "area": self.area, "ground_area": self.ground_area,
                "room_number": self.room_number, "floor_number": self.floor_number, "count_of_floors": self.count_of_floors, "kad_number": self.kad_number, "series": self.series,
                "house_type": self.house_type, "facilities": self.facilities, "purpose": self.purpose, "link": self.link}
