{
  "name": "Client",
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "description": "Nombre completo"
    },
    "email": {
      "type": "string",
      "description": "Email"
    },
    "phone": {
      "type": "string",
      "description": "Tel\u00e9fono"
    },
    "address": {
      "type": "string",
      "description": "Direcci\u00f3n"
    },
    "city": {
      "type": "string",
      "description": "Ciudad"
    },
    "notes": {
      "type": "string",
      "description": "Notas sobre el cliente"
    },
    "total_purchases": {
      "type": "number",
      "description": "Total de compras realizadas"
    },
    "is_online": {
      "type": "boolean",
      "default": false,
      "description": "Cliente registrado online"
    }
  },
  "required": [
    "name"
  ]
}
{
  "name": "Delivery",
  "type": "object",
  "properties": {
    "delivery_number": {
      "type": "string",
      "description": "N\u00famero de despacho"
    },
    "sale_id": {
      "type": "string",
      "description": "ID de la venta asociada"
    },
    "sale_number": {
      "type": "string"
    },
    "client_name": {
      "type": "string"
    },
    "client_phone": {
      "type": "string"
    },
    "client_address": {
      "type": "string"
    },
    "client_city": {
      "type": "string"
    },
    "items": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "product_name": {
            "type": "string"
          },
          "quantity": {
            "type": "number"
          }
        }
      }
    },
    "total": {
      {
  "name": "Employee",
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "description": "Nombre completo"
    },
    "role": {
      "type": "string",
      "enum": [
        "vendedor",
        "repartidor",
        "vendedor_repartidor"
      ],
      "description": "Rol del empleado"
    },
    "phone": {
      "type": "string",
      "description": "Tel\u00e9fono"
    },
    "commission_rate": {
      "type": "number",
      "description": "Porcentaje de comisi\u00f3n"
    },
    "is_active": {
      "type": "boolean",
      "default": true
    },
    "total_commissions_paid": {
      "type": "number",
      "description": "Total comisiones pagadas"
    },
    "total_commissions_pending": {
      "type": "number",
      "description": "Total comisiones pendientes"
    }
  },
  "required": [
    "name",
    "role"
  ]
