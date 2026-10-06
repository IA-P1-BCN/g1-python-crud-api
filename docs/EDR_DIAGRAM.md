# Diagrama ER — GymFlow

> Transcripción a Mermaid del diagrama original del cliente
> (`Diagrama_ER.png`, copiado en este repo como
> [Diagrama_ER.png](Diagrama_ER.png)). El diccionario de datos completo está en
> [DATABASE_SPEC.md](DATABASE_SPEC.md).

```mermaid
erDiagram
    CLIENTES ||--o{ PAGOS : "realiza"
    CLIENTES ||--o{ RESERVAS : "agenda"
    CLASES ||--o{ RESERVAS : "recibe"
    ENTRENADORES ||--o{ CLASES : "imparte"

    CLIENTES {
        int id_cliente PK "AUTO_INCREMENT"
        varchar nombre "VARCHAR(100) NOT NULL"
        varchar email UK "VARCHAR(150) UNIQUE"
        date fecha_inscripcion "solo PRD"
        varchar estado_membresia "VARCHAR(20): Activo | Inactivo | Suspendido"
    }

    ENTRENADORES {
        int id_entrenador PK "AUTO_INCREMENT"
        varchar nombre "VARCHAR(100) NOT NULL"
        varchar especialidad "VARCHAR(100)"
        varchar telefono "VARCHAR(20), solo PRD"
    }

    CLASES {
        int id_clase PK "AUTO_INCREMENT"
        varchar nombre_clase "VARCHAR(50) NOT NULL"
        datetime horario "NOT NULL"
        int capacidad_max "NOT NULL, aforo"
        int id_entrenador FK "hacia ENTRENADORES"
    }

    RESERVAS {
        int id_reserva PK "AUTO_INCREMENT"
        int id_cliente FK "hacia CLIENTES"
        int id_clase FK "hacia CLASES"
        datetime fecha_reserva "sello de tiempo"
        boolean asistio "DEFAULT FALSE"
    }

    PAGOS {
        int id_pago PK "AUTO_INCREMENT"
        int id_cliente FK "hacia CLIENTES"
        decimal monto "DECIMAL(10,2) NOT NULL"
        date fecha_pago "fecha de abono"
        varchar metodo_pago "VARCHAR(30): Tarjeta | Transferencia | Efectivo"
    }
```

## Lectura de las relaciones

| Relación | Mermaid | Significado |
|---|---|---|
| `CLIENTES` → `PAGOS` | `||--o{` | Un cliente realiza **cero o muchos** pagos; cada pago pertenece a **exactamente uno**. |
| `ENTRENADORES` → `CLASES` | `||--o{` | Un entrenador imparte cero o muchas clases; cada clase la dirige exactamente uno. |
| `CLIENTES` → `RESERVAS` | `||--o{` | Un cliente agenda cero o muchas reservas; cada reserva es de exactamente un cliente. |
| `CLASES` → `RESERVAS` | `||--o{` | Una clase recibe cero o muchas reservas (hasta el aforo); cada reserva apunta a una clase. |

La relación N:N original entre `CLIENTES` y `CLASES` queda resuelta por la
tabla intermedia `RESERVAS`, que aporta además los atributos propios de la
relación (`fecha_reserva`, `asistio`).
