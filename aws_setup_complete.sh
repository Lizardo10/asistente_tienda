#!/bin/bash
# aws_setup_complete.sh - Configuración completa de AWS

set -e

echo "🚀 Configuración completa de AWS para Asistente Tienda"
echo "=================================================="

# Variables de configuración
PROJECT_NAME="asistente-tienda"
REGION="us-east-1"
DOMAIN="tu-dominio.com"
EMAIL="tu-email@example.com"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${GREEN}[PASO $1]${NC} $2"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Función para crear recursos AWS
create_aws_resources() {
    print_step "1" "Creando recursos AWS..."
    
    # 1. S3 Bucket
    print_step "1.1" "Creando bucket S3..."
    BUCKET_NAME="${PROJECT_NAME}-imagenes-$(date +%s)"
    aws s3 mb s3://$BUCKET_NAME --region $REGION
    print_success "Bucket S3 creado: $BUCKET_NAME"
    
    # 2. Aurora PostgreSQL
    print_step "1.2" "Creando cluster Aurora PostgreSQL..."
    aws rds create-db-cluster \
        --db-cluster-identifier ${PROJECT_NAME}-db \
        --engine aurora-postgresql \
        --engine-version 13.7 \
        --master-username admin \
        --master-user-password $(openssl rand -base64 32) \
        --region $REGION \
        --backup-retention-period 7 \
        --storage-encrypted \
        --vpc-security-group-ids sg-default \
        --db-subnet-group-name default \
        --enable-cloudwatch-logs-exports postgresql
    
    print_success "Cluster Aurora PostgreSQL creado"
    
    # 3. ElastiCache Redis
    print_step "1.3" "Creando cluster Redis..."
    aws elasticache create-cache-cluster \
        --cache-cluster-id ${PROJECT_NAME}-redis \
        --cache-node-type cache.t3.micro \
        --engine redis \
        --num-cache-nodes 1 \
        --region $REGION
    
    print_success "Cluster Redis creado"
    
    # 4. CloudFront Distribution
    print_step "1.4" "Creando distribución CloudFront..."
    DISTRIBUTION_ID=$(aws cloudfront create-distribution \
        --distribution-config file://cloudfront_config.json \
        --query 'Distribution.Id' \
        --output text)
    
    print_success "Distribución CloudFront creada: $DISTRIBUTION_ID"
    
    # 5. WAF Web ACL
    print_step "1.5" "Creando WAF Web ACL..."
    WEB_ACL_ID=$(aws wafv2 create-web-acl \
        --name ${PROJECT_NAME}-waf \
        --scope CLOUDFRONT \
        --default-action Allow={} \
        --rules file://waf_rules.json \
        --region us-east-1 \
        --query 'Summary.Id' \
        --output text)
    
    print_success "WAF Web ACL creado: $WEB_ACL_ID"
}

# Función para configurar EC2
setup_ec2() {
    print_step "2" "Configurando instancia EC2..."
    
    # Crear security group
    print_step "2.1" "Creando security group..."
    SG_ID=$(aws ec2 create-security-group \
        --group-name ${PROJECT_NAME}-sg \
        --description "Security group para ${PROJECT_NAME}" \
        --query 'GroupId' \
        --output text)
    
    # Configurar reglas del security group
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 22 \
        --cidr 0.0.0.0/0
    
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 80 \
        --cidr 0.0.0.0/0
    
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 443 \
        --cidr 0.0.0.0/0
    
    print_success "Security group creado: $SG_ID"
    
    # Crear instancia EC2
    print_step "2.2" "Creando instancia EC2..."
    INSTANCE_ID=$(aws ec2 run-instances \
        --image-id ami-0c02fb55956c7d316 \
        --instance-type t2.micro \
        --key-name tu-clave \
        --security-group-ids $SG_ID \
        --subnet-id subnet-default \
        --user-data file://user_data.sh \
        --query 'Instances[0].InstanceId' \
        --output text)
    
    print_success "Instancia EC2 creada: $INSTANCE_ID"
    
    # Obtener IP pública
    PUBLIC_IP=$(aws ec2 describe-instances \
        --instance-ids $INSTANCE_ID \
        --query 'Reservations[0].Instances[0].PublicIpAddress' \
        --output text)
    
    print_success "IP pública: $PUBLIC_IP"
}

# Función para configurar monitoreo
setup_monitoring() {
    print_step "3" "Configurando monitoreo CloudWatch..."
    
    # Ejecutar script de monitoreo
    python3 cloudwatch_monitoring.py
    
    print_success "Monitoreo CloudWatch configurado"
}

# Función para generar archivos de configuración
generate_config_files() {
    print_step "4" "Generando archivos de configuración..."
    
    # Generar .env para producción
    cat > production.env << EOF
# Database
DATABASE_URL=postgresql://admin:password@aurora-cluster-endpoint:5432/asistente_tienda

# Redis
REDIS_URL=redis://elasticache-endpoint:6379

# AWS
AWS_ACCESS_KEY_ID=tu_access_key
AWS_SECRET_ACCESS_KEY=tu_secret_key
AWS_DEFAULT_REGION=us-east-1
S3_BUCKET_NAME=$BUCKET_NAME

# JWT
JWT_SECRET_KEY=$(openssl rand -base64 32)
JWT_ALGORITHM=HS256

# App
ENVIRONMENT=production
DEBUG=false
DOMAIN=$DOMAIN
EOF
    
    print_success "Archivo production.env generado"
}

# Función para mostrar resumen
show_summary() {
    print_step "5" "Resumen de la configuración"
    echo "=================================="
    echo "🌐 Dominio: $DOMAIN"
    echo "🪣 Bucket S3: $BUCKET_NAME"
    echo "🗄️  Base de datos: Aurora PostgreSQL"
    echo "🔄 Cache: Redis"
    echo "🌍 CDN: CloudFront"
    echo "🛡️  WAF: Configurado"
    echo "📊 Monitoreo: CloudWatch"
    echo ""
    print_warning "Recuerda actualizar las variables de entorno con los endpoints reales"
    print_warning "Configura tu dominio DNS para apuntar a la IP de EC2"
}

# Función principal
main() {
    echo "Iniciando configuración de AWS..."
    echo "Proyecto: $PROJECT_NAME"
    echo "Región: $REGION"
    echo "Dominio: $DOMAIN"
    echo ""
    
    # Verificar que AWS CLI esté configurado
    if ! aws sts get-caller-identity > /dev/null 2>&1; then
        print_error "AWS CLI no está configurado. Ejecuta 'aws configure' primero."
        exit 1
    fi
    
    # Crear recursos
    create_aws_resources
    setup_ec2
    setup_monitoring
    generate_config_files
    show_summary
    
    print_success "¡Configuración completada!"
    echo ""
    echo "Próximos pasos:"
    echo "1. Ejecutar: ./deploy_to_aws.sh"
    echo "2. Configurar DNS para tu dominio"
    echo "3. Configurar SSL con Let's Encrypt"
    echo "4. Probar la aplicación"
}

# Ejecutar función principal
main "$@"









