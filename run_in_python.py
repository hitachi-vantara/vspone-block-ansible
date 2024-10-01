# def calculate_naid(wwn_any_port, serial_number, lun, array_family=7):
#     wwn_any_port = int(wwn_any_port,16)
#     # Mask and adjustment based on array family
#     wwn_mask_and = 0xFFFFFF00
#     serial_number_mask_or = 0x00000000
    
#     if array_family == 0:  # ARRAY_FAMILY_DF
#         wwn_mask_and = 0xFFFFFFF0
#     elif array_family == 2:  # ARRAY_FAMILY_HM700
#         while serial_number > 99999:
#             serial_number -= 100000
#         serial_number_mask_or = 0x50200000
#     elif array_family == 3:  # ARRAY_FAMILY_R800
#         serial_number_mask_or = 0x00300000
#     elif array_family == 4:  # ARRAY_FAMILY_HM800
#         while serial_number > 99999:
#             serial_number -= 100000
#         serial_number_mask_or = 0x50400000
#     elif array_family == 5:  # ARRAY_FAMILY_R900
#         serial_number_mask_or = 0x00500000
#     elif array_family == 6:  # ARRAY_FAMILY_HM900
#         if 400000 <= serial_number < 500000:
#             serial_number_mask_or = 0x50400000
#         elif 700000 <= serial_number < 800000:
#             serial_number_mask_or = 0x50700000
#         else:
#             serial_number_mask_or = 0x50600000
#         while serial_number > 99999:
#             serial_number -= 100000
#     elif array_family == 7:  # ARRAY_FAMILY_HM2000
#         serial_number_mask_or = 0x50800000
#         while serial_number > 99999:
#             serial_number -= 100000
#     else:
#         raise ValueError(f"Unsupported array family: {array_family}")

#     # Apply masks
#     wwn_part = wwn_any_port & 0xFFFFFFFF
#     wwn_part &= wwn_mask_and
#     serial_number |= serial_number_mask_or

#     # Construct high bytes
#     high_bytes = (
#         (0x60 << 56) |
#         (0x06 << 48) |
#         (0x0e << 40) |
#         (0x80 << 32) |
#         ((wwn_part >> 24) & 0xFF) << 24 |
#         ((wwn_part >> 16) & 0xFF) << 16 |
#         ((wwn_part >> 8) & 0xFF) << 8 |
#         (wwn_part & 0xFF)
#     )

#     # Construct low bytes
#     low_bytes = (
#         ((serial_number >> 24) & 0xFF) << 56 |
#         ((serial_number >> 16) & 0xFF) << 48 |
#         ((serial_number >> 8) & 0xFF) << 40 |
#         (serial_number & 0xFF) << 32 |
#         0x00 << 24 |
#         0x00 << 16 |
#         ((lun >> 8) & 0xFF) << 8 |
#         (lun & 0xFF)
#     )

#     # Format NAID
#     naid = f"naa.{high_bytes:012x}{low_bytes:016x}"

#     return naid

# # Example usage
# # wwn_any_port = "50060E80089C4F00"
# wwn_any_port = "50060E80089C4F00"
# serial_number = 40015
# lun = 202
# array_family = 2

# naid = calculate_naid(wwn_any_port, serial_number, lun, 5)
# print(naid)  # Expected format: naa.60060e80282742005080274200000468

# #60060e80089c4f0000509c4f000000c5
# #60060e80089c4f0050609c4f000000c5


# Define the mapping of device types to array families
# Define the mapping of individual device types to array families
array_family_lookup = {
    "AMS": "ARRAY_FAMILY_DF",
    "HUS": "ARRAY_FAMILY_DF",
    "VSP": "ARRAY_FAMILY_R700",
    "HUS-VM": "ARRAY_FAMILY_HM700",
    "VSP G1000": "ARRAY_FAMILY_R800",
    "VSP G1500/F1500": "ARRAY_FAMILY_R800",
    "VSP G200": "ARRAY_FAMILY_HM800",
    "VSP G 400": "ARRAY_FAMILY_HM800",
    "VSP F 400": "ARRAY_FAMILY_HM800",
    "VSP N 400": "ARRAY_FAMILY_HM800",
    "VSP G 600": "ARRAY_FAMILY_HM800",
    "VSP F 600": "ARRAY_FAMILY_HM800",
    "VSP N 600": "ARRAY_FAMILY_HM800",
    "VSP G 800": "ARRAY_FAMILY_HM800",
    "VSP F 800": "ARRAY_FAMILY_HM800",
    "VSP N 800": "ARRAY_FAMILY_HM800",
    "VSP G130": "ARRAY_FAMILY_HM800",
    "VSP G150": "ARRAY_FAMILY_HM800",
    "VSP G/F350": "ARRAY_FAMILY_HM800",
    "VSP G/F370": "ARRAY_FAMILY_HM800",
    "VSP G/F700": "ARRAY_FAMILY_HM800",
    "VSP G/F900": "ARRAY_FAMILY_HM800",
    "VSP 5000": "ARRAY_FAMILY_R900",
    "VSP 5000H": "ARRAY_FAMILY_R900",
    "VSP 5500": "ARRAY_FAMILY_R900",
    "VSP 5500H": "ARRAY_FAMILY_R900",
    "VSP 5200": "ARRAY_FAMILY_R900",
    "VSP 5200H": "ARRAY_FAMILY_R900",
    "VSP 5600": "ARRAY_FAMILY_R900",
    "VSP 5600H": "ARRAY_FAMILY_R900",
    "VSP E590": "ARRAY_FAMILY_HM900",
    "VSP E790": "ARRAY_FAMILY_HM900",
    "VSP E990": "ARRAY_FAMILY_HM900",
    "VSP E1090": "ARRAY_FAMILY_HM900",
    "VSP E1090H": "ARRAY_FAMILY_HM900",
    "VSP One B23": "ARRAY_FAMILY_HM2000",
    "VSP One B24": "ARRAY_FAMILY_HM2000",
    "VSP One B26": "ARRAY_FAMILY_HM2000",
    "VSP One B28": "ARRAY_FAMILY_HM2000",
}

def get_array_family(model):
    return array_family_lookup.get(model, "Unknown array family")

# Example usage
model = "VSP 5600H"
array_family = get_array_family(model)
print(f"The array family for storage device type '{model}' is: {array_family}")
