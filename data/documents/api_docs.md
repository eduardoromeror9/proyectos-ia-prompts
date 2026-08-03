# Documentación de la API

## Rate Limits

El límite de rate en nuestra API es de 1000 requests por minuto por usuario. Si lo superas recibirás un error 429. Implementa exponential backoff en el cliente.