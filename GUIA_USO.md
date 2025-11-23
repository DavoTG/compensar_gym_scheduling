# 🚀 Guía de Configuración y Uso

## Paso 1: Configurar Credenciales

1. Copia el archivo `.env.example` y renómbralo a `.env`:
   ```bash
   copy .env.example .env
   ```

2. Abre el archivo `.env` y completa tu contraseña:
   ```
   DOCUMENT_TYPE=CC
   DOCUMENT_NUMBER=1022363309
   PASSWORD=tu_contraseña_aqui
   DEBUG=True
   ```

## Paso 2: Instalar Dependencias

Las dependencias ya están instaladas. Si necesitas reinstalarlas:
```bash
pip install -r requirements.txt
```

## Paso 3: Ejecutar la Aplicación

```bash
python main.py
```

## 📖 Cómo Usar la Aplicación

### Flujo de Trabajo

1. **Login Automático**: La aplicación se conecta automáticamente con tus credenciales

2. **Menú Principal**:
   ```
   1. 📅 Agregar reservas
   2. 👀 Ver reservas pendientes
   3. ✅ Confirmar y ejecutar reservas
   4. 🗑️  Limpiar reservas pendientes
   5. 🚪 Salir
   ```

3. **Agregar Reservas**:
   - Selecciona una tiquetera (gimnasio, clase grupal, natación)
   - Selecciona las fechas (puedes elegir múltiples días)
   - Para cada fecha, selecciona los horarios que desees
   - Las reservas se agregan a una lista pendiente

4. **Ver Reservas Pendientes**:
   - Muestra todas las reservas que has agregado pero aún no has confirmado

5. **Confirmar y Ejecutar**:
   - Muestra un resumen de todas las reservas
   - Pide confirmación
   - Ejecuta TODAS las reservas de una vez

### Ejemplo de Uso

```
Quiero reservar:
- Gimnasio Cajicá: Lunes 10:00, Miércoles 10:00, Viernes 10:00
- Natación CUR: Martes 18:00, Jueves 18:00

Pasos:
1. Selecciono opción 1 (Agregar reservas)
2. Selecciono "Gimnasio Cajicá"
3. Selecciono fechas: 1,3,5 (Lunes, Miércoles, Viernes)
4. Para cada fecha, selecciono el horario 10:00
5. Vuelvo al menú y selecciono opción 1 nuevamente
6. Selecciono "Natación CUR"
7. Selecciono fechas: 2,4 (Martes, Jueves)
8. Para cada fecha, selecciono el horario 18:00
9. Selecciono opción 2 para ver mis 5 reservas pendientes
10. Selecciono opción 3 para confirmar y ejecutar TODAS a la vez
```

## ⚠️ Notas Importantes

### Autenticación
- El sistema utiliza las mismas APIs que la página web de Compensar
- Las cookies de sesión se manejan automáticamente
- Si el login falla, verifica tus credenciales en el archivo `.env`

### Tiqueteras
- El sistema obtiene automáticamente todas tus tiqueteras activas
- Cada tiquetera corresponde a una sede y tipo de actividad
- El `id_participacion_deportista` se obtiene automáticamente

### Horarios
- Los horarios se obtienen en tiempo real de la API
- Solo se muestran horarios con cupos disponibles
- Puedes seleccionar múltiples horarios para múltiples fechas

### Reservas Múltiples
- **Esta es la ventaja principal**: Puedes agregar todas las reservas que quieras antes de confirmar
- Una vez confirmas, se ejecutan TODAS de forma automática
- El sistema muestra un resumen de exitosas/fallidas

## 🔧 Solución de Problemas

### Error de Login
```
❌ Login fallido - Verifica tus credenciales
```
**Solución**: Verifica que tu contraseña en `.env` sea correcta

### No se encuentran tiqueteras
```
❌ No se encontraron tiqueteras disponibles
```
**Solución**: Verifica que tu membresía esté activa en Compensar

### Error al obtener horarios
```
❌ Error obteniendo horarios
```
**Solución**: 
- Verifica tu conexión a internet
- Intenta con otra fecha
- Activa DEBUG=True en `.env` para ver más detalles

## 🐛 Modo Debug

Para ver información detallada de errores, activa el modo debug en `.env`:
```
DEBUG=True
```

Esto mostrará:
- Trazas completas de errores
- Información de requests HTTP
- Detalles de la API

## 📝 Estructura de Datos

### Tiquetera
```python
{
    "id": 131525755,
    "nombre_centro_entrenamiento": "Gimnasio Cajicá",
    "nombre_sede": "Cajicá",
    "nombre_deporte": "Acondicionamiento",
    "id_centro_entrenamiento": 183,
    "id_participacion_deportista": 4626802,
    "entradas": 9223372036854776000,
    "ilimitado": true
}
```

### Horario
```python
{
    "fecha": "2025-11-23",
    "hora_inicio": "10:00",
    "hora_fin": "11:00",
    "cupos_disponibles": 20,
    "id_turno": 12345
}
```

### Reserva
```python
{
    "id_centro_entrenamiento": 183,
    "id_participacion_deportista": 4626802,
    "fecha": "2025-11-23",
    "hora_inicio": "10:00",
    "hora_fin": "11:00",
    "id_turno": 12345
}
```

## 🎯 Próximas Mejoras

- [ ] Guardar configuraciones de reservas favoritas
- [ ] Programar reservas automáticas recurrentes
- [ ] Notificaciones cuando se abren nuevos cupos
- [ ] Interfaz gráfica (GUI)
- [ ] Exportar historial de reservas

## 📞 Soporte

Si encuentras algún problema:
1. Activa `DEBUG=True` en `.env`
2. Ejecuta nuevamente y copia el error completo
3. Verifica que la página web de Compensar esté funcionando
