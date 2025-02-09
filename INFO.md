# 📋 Informe Técnico de Diseño

## Decisiones de Arquitectura

### 1. Modelo Cliente-Servidor
- **Decisión**: Arquitectura distribuida con servidor central y clientes ligeros
- **Justificación**: Permite centralizar recursos computacionales y facilita escalabilidad

### 2. Sistema de Cola (Celery + Redis)
- **Decisión**: Implementación de cola de tareas distribuida
- **Justificación**: 
  - Manejo eficiente de múltiples solicitudes
  - Prevención de sobrecarga del servidor
  - Procesamiento asíncrono de tareas pesadas

### 3. Soporte Dual IP (IPv4/IPv6)
- **Decisión**: Implementación simultánea de ambos protocolos
- **Justificación**: Compatibilidad futura y soporte legacy

### 4. Almacenamiento de Imágenes
- **Decisión**: Sistema de archivos local con UUIDs
- **Justificación**: 
  - Simplicidad de implementación
  - Fácil backup y mantenimiento
  - Identificadores únicos para evitar colisiones

### 5. Logging Separado
- **Decisión**: Proceso independiente para logging
- **Justificación**: 
  - Evita bloqueos en operaciones I/O
  - Mejor rendimiento del servidor principal

### 6. Cliente Asíncrono
- **Decisión**: Implementación de cliente con requests asíncronos
- **Justificación**: Mejor experiencia de usuario durante generación de imágenes

## Tecnologías Utilizadas

### Stable Diffusion
- **Uso**: Generación de imágenes
- **Justificación**: Modelo estado del arte, buena relación calidad/rendimiento

### aiohttp
- **Uso**: Servidor web asíncrono
- **Justificación**: Alto rendimiento y manejo eficiente de conexiones

### Redis
- **Uso**: Backend de cola y caché
- **Justificación**: Rápido, confiable y ampliamente probado
