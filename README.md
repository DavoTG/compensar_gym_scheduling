# Compensar Gym Scheduler

Sistema automatizado para agendar múltiples clases/gimnasio/piscina en Compensar de forma simultánea con **interfaz web**.

## 🌟 Características

- ✅ **Interfaz Web Moderna**: Login y dashboard intuitivos
- ✅ **Multi-usuario**: Cualquier persona puede usar el sistema con sus propias credenciales
- ✅ **Login Seguro**: Credenciales ingresadas directamente en la página (no se almacenan)
- ✅ **Selección Múltiple**: Agrega todas las reservas que quieras antes de confirmar
- ✅ **Ejecución en Batch**: Confirma y ejecuta todas las reservas a la vez
- ✅ **Entorno Virtual**: Dependencias aisladas del sistema

## 📦 Estructura del Proyecto

```
Gym scheduling/
├── 📄 app.py                         # Aplicación web Flask
├── 📄 start.bat                      # Script de inicio (Windows)
├── 📄 setup_venv.bat                 # Configuración del entorno virtual
├── 📄 requirements.txt               # Dependencias
├── 📁 venv/                          # Entorno virtual (auto-generado)
├── 📁 templates/                     # Plantillas HTML
│   ├── base.html
│   ├── login.html
│   └── dashboard.html
├── 📁 config/                        # Configuración
│   └── config.py
└── 📁 src/                           # Código fuente
    ├── auth/                         # Autenticación
    ├── api/                          # API de Compensar
    ├── models/                       # Modelos de datos
    └── scheduler/                    # Lógica de agendamiento
```

## 🚀 Instalación y Uso

### Opción 1: Inicio Rápido (Recomendado)

1. **Doble clic en `start.bat`**
   - Esto configurará automáticamente el entorno virtual
   - Instalará las dependencias
   - Iniciará el servidor web

2. **Abre tu navegador en:**
   ```
   http://localhost:5000
   ```

3. **Ingresa tus credenciales de Compensar**

### Opción 2: Configuración Manual

1. **Configurar entorno virtual:**
   ```bash
   setup_venv.bat
   ```

2. **Iniciar aplicación:**
   ```bash
   start.bat
   ```

## 💻 Uso de la Aplicación Web

### 1. Login
- Ingresa tu tipo de documento (CC, TI, CE, PA)
- Ingresa tu número de documento
- Ingresa tu contraseña de Compensar
- Click en "Ingresar"

### 2. Dashboard
El dashboard tiene dos paneles:

**Panel Izquierdo - Selección:**
- Ver todas tus tiqueteras organizadas por deporte
- Seleccionar una actividad (gimnasio, clase grupal, natación)
- Seleccionar fecha
- Ver horarios disponibles
- Click en un horario para agregarlo

**Panel Derecho - Reservas Pendientes:**
- Ver todas las reservas que has agregado
- Eliminar reservas individuales
- Confirmar y ejecutar TODAS las reservas a la vez
- Limpiar todas las reservas pendientes

### 3. Flujo de Trabajo

```
1. Login con tus credenciales
2. Selecciona una actividad (ej: Gimnasio Cajicá)
3. Selecciona una fecha
4. Click en los horarios que desees
5. Repite para otras actividades/fechas
6. Revisa tus reservas pendientes
7. Click en "Confirmar Todas"
8. ¡Listo! Todas las reservas se ejecutan automáticamente
```

## 🎯 Ventajas vs Página Web Original

| Antes (Web Compensar) | Ahora (Este Sistema) |
|----------------------|---------------------|
| 1 reserva a la vez | ✅ Múltiples reservas simultáneas |
| Repetir proceso para cada reserva | ✅ Agregar todas, confirmar una vez |
| ~5 minutos por reserva | ✅ ~30 segundos para 10 reservas |
| Solo desde tu PC | ✅ Accesible desde cualquier dispositivo |
| Credenciales en archivo | ✅ Login directo en la página |

## 🔒 Seguridad

- ✅ Las credenciales **NO se almacenan** en archivos
- ✅ Las sesiones expiran después de 2 horas de inactividad
- ✅ Cada usuario tiene su propia sesión independiente
- ✅ Conexión directa con la API oficial de Compensar

## 🛠️ Requisitos

- Python 3.7 o superior
- Windows (los scripts .bat son para Windows)
- Conexión a internet
- Membresía activa en Compensar

## 📱 Acceso desde Otros Dispositivos

Para acceder desde otros dispositivos en tu red local:

1. Encuentra tu IP local:
   ```bash
   ipconfig
   ```
   Busca "IPv4 Address" (ej: 192.168.1.100)

2. En otros dispositivos, abre:
   ```
   http://TU_IP:5000
   ```
   (ej: http://192.168.1.100:5000)

## 🐛 Solución de Problemas

### Error al iniciar
```bash
# Reinstalar dependencias
setup_venv.bat
```

### Puerto 5000 ocupado
Edita `app.py` y cambia el puerto:
```python
app.run(debug=True, host='0.0.0.0', port=8080)
```

### Error de login
- Verifica que tus credenciales sean correctas
- Verifica que la página web de Compensar esté funcionando
- Intenta cerrar sesión y volver a iniciar

## 📚 Documentación Adicional

- `GUIA_USO.md`: Guía detallada de uso
- `PROYECTO_RESUMEN.md`: Resumen técnico completo

## 🎓 Tecnologías Utilizadas

- **Backend**: Python + Flask
- **Frontend**: HTML + CSS + JavaScript
- **API**: Requests (interacción con Compensar)
- **Sesiones**: Flask-Session

## 🔄 Actualizaciones

Para actualizar el proyecto:
```bash
git pull
setup_venv.bat
```

## 📞 Soporte

Si encuentras problemas:
1. Verifica que la página web de Compensar funcione
2. Revisa los mensajes de error en la consola
3. Intenta reiniciar el servidor

## ⚠️ Notas Importantes

- Este sistema usa las mismas APIs que la página web oficial
- Respeta los límites de tu membresía
- No hagas spam de reservas
- Cancela las reservas que no uses

## 🎉 ¡Disfruta!

Ahora puedes hacer tus reservas de forma rápida y eficiente. ¡A entrenar! 🏋️‍♂️🏊‍♂️

---

**Inicio rápido:** Doble click en `start.bat` → Abre http://localhost:5000 → ¡Listo!
