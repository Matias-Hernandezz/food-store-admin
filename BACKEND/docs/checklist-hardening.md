# Checklist hardening (borrador M0.3)

Marcá cuando esté hecho en el entorno de producción real.

## Servidor
- [ ] Usuario SSH sin root, llave única, `PasswordAuthentication no`
- [ ] `ufw`: 22, 80, 443
- [ ] `fail2ban`, `unattended-upgrades`
- [ ] Zona horaria `America/Argentina/Buenos_Aires`
- [ ] Swap si RAM &lt; 4 GB

## Docker
- [ ] Imágenes con tag de versión (no `latest` en prod)
- [ ] Límites CPU/RAM por servicio
- [ ] Rotación de logs (`json-file` max-size)
- [ ] Postgres y Redis sin puertos publicados en prod

## Secretos
- [ ] `.env.production` fuera del repo, permisos 600
- [ ] `SECRET_KEY` y passwords rotados respecto a dev
- [ ] Redis con contraseña en prod

## App
- [ ] `TENANT_MODE=multi` + DB `foodstore_control` migrada
- [ ] `REDIS_URL` con multi-worker
- [ ] CORS solo dominios del cliente
- [ ] `SECURE_COOKIES=true` detrás de HTTPS
- [ ] Backups probados (restore mensual)

## Monitoreo
- [ ] Healthcheck `/health` en uptime
- [ ] Alerta disco &gt; 80%
- [ ] Alerta backup fallido
