# cloudwatch_monitoring.py
import boto3
import json
from datetime import datetime, timedelta

class CloudWatchMonitoring:
    def __init__(self):
        self.cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')
        self.logs = boto3.client('logs', region_name='us-east-1')
    
    def create_custom_metrics(self):
        """Crear métricas personalizadas para la aplicación"""
        
        # Métricas de aplicación
        metrics = [
            {
                'Namespace': 'AsistenteTienda/Application',
                'MetricName': 'ImageAnalysisCount',
                'Unit': 'Count',
                'Description': 'Número de imágenes analizadas'
            },
            {
                'Namespace': 'AsistenteTienda/Application', 
                'MetricName': 'ChatMessagesCount',
                'Unit': 'Count',
                'Description': 'Número de mensajes de chat procesados'
            },
            {
                'Namespace': 'AsistenteTienda/Application',
                'MetricName': 'ResponseTime',
                'Unit': 'Milliseconds',
                'Description': 'Tiempo de respuesta promedio'
            },
            {
                'Namespace': 'AsistenteTienda/Application',
                'MetricName': 'ErrorRate',
                'Unit': 'Percent',
                'Description': 'Tasa de errores'
            }
        ]
        
        for metric in metrics:
            try:
                self.cloudwatch.put_metric_data(
                    Namespace=metric['Namespace'],
                    MetricData=[{
                        'MetricName': metric['MetricName'],
                        'Value': 0,
                        'Unit': metric['Unit'],
                        'Timestamp': datetime.utcnow()
                    }]
                )
                print(f"✅ Métrica creada: {metric['MetricName']}")
            except Exception as e:
                print(f"❌ Error creando métrica {metric['MetricName']}: {e}")
    
    def create_alarms(self):
        """Crear alarmas para monitoreo"""
        
        alarms = [
            {
                'AlarmName': 'HighErrorRate',
                'AlarmDescription': 'Alta tasa de errores en la aplicación',
                'MetricName': 'ErrorRate',
                'Namespace': 'AsistenteTienda/Application',
                'Statistic': 'Average',
                'Period': 300,
                'EvaluationPeriods': 2,
                'Threshold': 5.0,
                'ComparisonOperator': 'GreaterThanThreshold'
            },
            {
                'AlarmName': 'HighResponseTime',
                'AlarmDescription': 'Tiempo de respuesta alto',
                'MetricName': 'ResponseTime',
                'Namespace': 'AsistenteTienda/Application',
                'Statistic': 'Average',
                'Period': 300,
                'EvaluationPeriods': 2,
                'Threshold': 5000.0,
                'ComparisonOperator': 'GreaterThanThreshold'
            },
            {
                'AlarmName': 'HighCPUUtilization',
                'AlarmDescription': 'Alto uso de CPU en EC2',
                'MetricName': 'CPUUtilization',
                'Namespace': 'AWS/EC2',
                'Statistic': 'Average',
                'Period': 300,
                'EvaluationPeriods': 2,
                'Threshold': 80.0,
                'ComparisonOperator': 'GreaterThanThreshold',
                'Dimensions': [
                    {
                        'Name': 'InstanceId',
                        'Value': 'tu-instance-id'
                    }
                ]
            }
        ]
        
        for alarm in alarms:
            try:
                self.cloudwatch.put_metric_alarm(**alarm)
                print(f"✅ Alarma creada: {alarm['AlarmName']}")
            except Exception as e:
                print(f"❌ Error creando alarma {alarm['AlarmName']}: {e}")
    
    def create_log_groups(self):
        """Crear grupos de logs"""
        
        log_groups = [
            '/aws/ec2/asistente-tienda/application',
            '/aws/ec2/asistente-tienda/nginx',
            '/aws/ec2/asistente-tienda/system'
        ]
        
        for log_group in log_groups:
            try:
                self.logs.create_log_group(logGroupName=log_group)
                print(f"✅ Grupo de logs creado: {log_group}")
            except self.logs.exceptions.ResourceAlreadyExistsException:
                print(f"ℹ️ Grupo de logs ya existe: {log_group}")
            except Exception as e:
                print(f"❌ Error creando grupo de logs {log_group}: {e}")

# Script para configurar monitoreo
if __name__ == "__main__":
    monitoring = CloudWatchMonitoring()
    
    print("🔍 Configurando monitoreo CloudWatch...")
    
    print("\n📊 Creando métricas personalizadas...")
    monitoring.create_custom_metrics()
    
    print("\n🚨 Creando alarmas...")
    monitoring.create_alarms()
    
    print("\n📝 Creando grupos de logs...")
    monitoring.create_log_groups()
    
    print("\n✅ Configuración de monitoreo completada!")









