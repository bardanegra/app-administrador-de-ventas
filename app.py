{
  "name": "BusinessSettings",
  "type": "object",
  "properties": {
    "business_name": {
      "type": "string",
      "description": "Nombre del negocio"
    },
    "default_commission_seller": {
      "type": "number",
      "description": "Comisi\u00f3n vendedor % por defecto"
    },
    "default_commission_delivery": {
      "type": "number",
      "description": "Comisi\u00f3n repartidor % por defecto"
    },
    "installment_fee_3": {
      "type": "number",
      "description": "Descuento % por 3 cuotas sin inter\u00e9s"
    },
    "installment_fee_6": {
      "type": "number",
      "description": "Descuento % por 6 cuotas sin inter\u00e9s"
    },
    "installment_fee_12": {
      "type": "number",
      "description": "Descuento % por 12 cuotas sin inter\u00e9s"
    },
    "default_shipping_cost": {
      "type": "number",
      "description": "Costo env\u00edo por defecto"
    },
    "savings_percent": {
      "type": "number",
      "description": "% destinado a ahorro/inversi\u00f3n"
    },
    "cost_percent": {
      "type": "number",
      "description": "% estimado de costo sobre precio final"
    },
    "settings_key": {
      "type": "string",
      "default": "main",
      "description": "Clave \u00fanica de configuraci\u00f3n"
    }
  },
  "required": [
    "settings_key"
  ]
}
