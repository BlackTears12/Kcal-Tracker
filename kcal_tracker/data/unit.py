from dataclasses import dataclass, field

weight_units: list[str] = ["g", "dkg", "kg"]
volume_units: list[str] = ["ml", "dl", "l"]

weight_conversion_factors: list[int] = [1, 10, 1000]
volume_conversion_factors: list[int] = [1, 100, 1000]

unit_conversion_factors: list[int] = [1, 10, 1000]

ALL_UNITS = weight_units + volume_units + ["serving"]

@dataclass
class Unit:
    unit: str = "g"

    def conversion_factor(self, convert_to) -> float:
        self_factor = 1.0
        convert_factor = 1.0
        if self.unit in weight_units and convert_to.unit in weight_units:
            self_factor = weight_conversion_factors[weight_units.index(self.unit)]
            convert_factor = weight_conversion_factors[weight_units.index(convert_to.unit)]
            return self_factor / convert_factor
        if self.unit in volume_units and convert_to.unit in volume_units:
            self_factor = volume_conversion_factors[volume_units.index(self.unit)]
            convert_factor = volume_conversion_factors[volume_units.index(convert_to.unit)]
            return self_factor / convert_factor
        if self.unit == convert_to.unit:
            return 1.0
        return 1.0