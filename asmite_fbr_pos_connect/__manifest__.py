{
    "name": "ASMIte FBR PoS Connect",
    "version": "16.0.1.0.0",  # Versioning based on Odoo version 16
    "author": "ASMIte Inc",
    "category": "Custom",
    "depends": ["sale", "account"],
    "data": [
        "views/asmite_fbr_pos_connect_view.xml"
    ],
    "installable": True,
    "application": True,
    "license": "LGPL-3",
    "summary": "FBR POS Integration for Pakistan",
    "description": "This app integrates Odoo with the FBR POS system to handle tax calculations and reporting in Pakistan."
}
