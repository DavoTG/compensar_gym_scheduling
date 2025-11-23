# 🚀 INICIO RÁPIDO - Compensar Gym Scheduler

## ⚡ 3 Pasos para Empezar

### 1️⃣ Doble Click en `start.bat`

```
📁 Gym scheduling/
   📄 start.bat  ← ¡DOBLE CLICK AQUÍ!
```

Esto abrirá una ventana que dice:
```
========================================
  Compensar Gym Scheduler - Inicio
========================================

Iniciando servidor web...

La aplicacion estara disponible en:
  http://localhost:5000

Presiona Ctrl+C para detener el servidor
```

### 2️⃣ Abre tu Navegador

Abre cualquier navegador (Chrome, Firefox, Edge) y ve a:

```
http://localhost:5000
```

### 3️⃣ Ingresa tus Credenciales

Verás una página de login donde debes ingresar:
- **Tipo de Documento**: CC (o el que uses)
- **Número de Documento**: Tu número de cédula
- **Contraseña**: Tu contraseña de Compensar

¡Y listo! Ya puedes empezar a hacer reservas.

---

## 🎯 Cómo Hacer Reservas

### Ejemplo: Reservar Gimnasio para la Semana

1. **Login** con tus credenciales ✅

2. **Selecciona "Gimnasio Cajicá"** (o el que prefieras)
   - Click en la actividad en el panel izquierdo

3. **Selecciona la fecha** (ej: Lunes)
   - Usa el selector de fecha

4. **Click en el horario** que desees (ej: 10:00 - 11:00)
   - El horario se agrega a "Reservas Pendientes"

5. **Repite** para otros días:
   - Selecciona Martes → Click en 10:00 - 11:00
   - Selecciona Miércoles → Click en 10:00 - 11:00
   - etc.

6. **Revisa** tus reservas en el panel derecho
   - Verás todas las reservas que agregaste

7. **Click en "✅ Confirmar Todas"**
   - Todas las reservas se ejecutan automáticamente
   - Recibes un resumen: Exitosas / Fallidas

---

## 💡 Consejos

### ✅ Puedes Mezclar Actividades

```
Lunes:    Gimnasio Cajicá 10:00
Martes:   Natación CUR 18:00
Miércoles: Clase Grupal 94 19:00
Jueves:   Gimnasio Cajicá 10:00
Viernes:  Natación CUR 18:00
```

Agrega todas, confirma una vez, ¡listo!

### ✅ Elimina Reservas Antes de Confirmar

Si te equivocaste, puedes eliminar reservas individuales antes de confirmar.

### ✅ Usa desde Cualquier Dispositivo

- Desde tu PC: `http://localhost:5000`
- Desde tu celular/tablet (en la misma red):
  1. Averigua tu IP: `ipconfig` en CMD
  2. Abre `http://TU_IP:5000` en el celular

---

## 🔒 Seguridad

- ✅ Tus credenciales NO se guardan en ningún archivo
- ✅ Solo se usan para conectarte a Compensar
- ✅ La sesión expira después de 2 horas
- ✅ Cada persona usa sus propias credenciales

---

## ❓ Preguntas Frecuentes

### ¿Necesito configurar algo antes de usar?

**No.** Solo ejecuta `start.bat` y ya.

### ¿Puedo usarlo varias personas?

**Sí.** Cada persona ingresa con sus propias credenciales.

### ¿Funciona en Mac/Linux?

Los scripts `.bat` son para Windows. En Mac/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

### ¿Qué pasa si cierro la ventana negra?

El servidor se detiene. Para volver a usar, ejecuta `start.bat` nuevamente.

### ¿Es seguro?

Sí. Usa las mismas APIs que la página oficial de Compensar.

---

## 🆘 Ayuda

### Error: "No se puede conectar"

1. Verifica que la ventana negra (servidor) esté abierta
2. Verifica que la URL sea `http://localhost:5000`
3. Intenta cerrar y abrir el navegador

### Error: "Credenciales incorrectas"

1. Verifica tu documento y contraseña
2. Intenta iniciar sesión en la página web de Compensar
3. Si funciona allá, debería funcionar aquí

### Error: "Puerto 5000 ocupado"

Otro programa está usando el puerto 5000. Opciones:
1. Cierra otros programas que puedan usar ese puerto
2. O edita `app.py` y cambia `port=5000` a `port=8080`

---

## 🎉 ¡Eso es Todo!

**Recuerda:**
1. `start.bat` → Inicia el servidor
2. `http://localhost:5000` → Abre en navegador
3. Login → Seleccionar → Agregar → Confirmar

**¡Disfruta de tus reservas automatizadas!** 🏋️‍♂️🏊‍♂️
