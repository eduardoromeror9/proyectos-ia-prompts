# Guía de Deploy

## DevOps

Para hacer deploy a producción:

1. Corre los tests con pytest.
2. Build la imagen Docker.
3. Push al registry.
4. Aplica el helm chart con kubectl.