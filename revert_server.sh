#!/bin/bash

echo "🔄 Revirtiendo configuración del servidor..."

# Detener servicios
sudo systemctl stop asistente-backend
sudo systemctl disable asistente-backend
sudo systemctl stop nginx
sudo systemctl disable nginx

# Eliminar archivos de configuración
sudo rm -f /etc/systemd/system/asistente-backend.service
sudo rm -f /etc/nginx/sites-available/asistente-tienda
sudo rm -f /etc/nginx/sites-enabled/asistente-tienda
sudo rm -rf /var/www/asistente-tienda

# Restaurar configuración por defecto
sudo ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/
sudo systemctl restart nginx

# Limpiar archivos de la aplicación
sudo rm -rf /home/ubuntu/asistente_tienda

echo "✅ Configuración revertida exitosamente"






