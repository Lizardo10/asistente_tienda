#!/bin/bash
# deploy_to_aws.sh - Script de despliegue automático

set -e

echo "🚀 Iniciando despliegue a AWS..."

# Variables
EC2_INSTANCE_IP="tu-ip-ec2"
EC2_KEY_PATH="tu-clave.pem"
GITHUB_REPO="https://github.com/Lizardo10/asistente_tienda.git"

# 1. Conectar a EC2 y actualizar sistema
echo "📦 Actualizando sistema en EC2..."
ssh -i $EC2_KEY_PATH ubuntu@$EC2_INSTANCE_IP << 'EOF'
    sudo apt update
    sudo apt upgrade -y
    
    # Instalar dependencias del sistema
    sudo apt install -y python3-pip python3-venv nginx redis-server git
    
    # Instalar Node.js 18
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
EOF

# 2. Clonar/actualizar repositorio
echo "📥 Clonando repositorio..."
ssh -i $EC2_KEY_PATH ubuntu@$EC2_INSTANCE_IP << EOF
    if [ -d "asistente_tienda" ]; then
        cd asistente_tienda
        git pull origin main
    else
        git clone $GITHUB_REPO
        cd asistente_tienda
    fi
EOF

# 3. Configurar Backend
echo "🔧 Configurando backend..."
ssh -i $EC2_KEY_PATH ubuntu@$EC2_INSTANCE_IP << 'EOF'
    cd asistente_tienda/backend
    
    # Crear entorno virtual
    python3 -m venv .venv
    source .venv/bin/activate
    
    # Instalar dependencias
    pip install -r requirements_aws.txt
    
    # Configurar variables de entorno
    cat > .env << 'ENVEOF'
# Database
DATABASE_URL=postgresql://admin:password@aurora-cluster-endpoint:5432/asistente_tienda

# Redis
REDIS_URL=redis://elasticache-endpoint:6379

# AWS
AWS_ACCESS_KEY_ID=tu_access_key
AWS_SECRET_ACCESS_KEY=tu_secret_key
AWS_DEFAULT_REGION=us-east-1
S3_BUCKET_NAME=asistente-tienda-imagenes

# JWT
JWT_SECRET_KEY=tu_jwt_secret_super_seguro
JWT_ALGORITHM=HS256

# OpenAI (opcional)
OPENAI_API_KEY=tu_openai_key

# App
ENVIRONMENT=production
DEBUG=false
ENVEOF
    
    # Inicializar base de datos
    python init_db.py
    
    # Crear servicio systemd
    sudo tee /etc/systemd/system/asistente-backend.service > /dev/null << 'SERVICEEOF'
[Unit]
Description=Asistente Tienda Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/asistente_tienda/backend
Environment=PATH=/home/ubuntu/asistente_tienda/backend/.venv/bin
ExecStart=/home/ubuntu/asistente_tienda/backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
SERVICEEOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable asistente-backend
    sudo systemctl start asistente-backend
EOF

# 4. Configurar Frontend
echo "🎨 Configurando frontend..."
ssh -i $EC2_KEY_PATH ubuntu@$EC2_INSTANCE_IP << 'EOF'
    cd asistente_tienda/frontend
    
    # Instalar dependencias
    npm install
    
    # Configurar variables de entorno
    cat > .env << 'ENVEOF'
VITE_API_BASE=https://tu-dominio.com/api
VITE_WS_URL=wss://tu-dominio.com/ws
ENVEOF
    
    # Build para producción
    npm run build
    
    # Configurar Nginx
    sudo tee /etc/nginx/sites-available/asistente-tienda > /dev/null << 'NGINXEOF'
server {
    listen 80;
    server_name tu-dominio.com www.tu-dominio.com;
    
    # Frontend
    location / {
        root /home/ubuntu/asistente_tienda/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # API Backend
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
    
    # WebSocket
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINXEOF
    
    sudo ln -sf /etc/nginx/sites-available/asistente-tienda /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    sudo nginx -t
    sudo systemctl reload nginx
EOF

# 5. Configurar SSL con Let's Encrypt
echo "🔒 Configurando SSL..."
ssh -i $EC2_KEY_PATH ubuntu@$EC2_INSTANCE_IP << 'EOF'
    sudo apt install -y certbot python3-certbot-nginx
    sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com --non-interactive --agree-tos --email tu-email@example.com
EOF

echo "✅ Despliegue completado!"
echo "🌐 Tu aplicación está disponible en: https://tu-dominio.com"









