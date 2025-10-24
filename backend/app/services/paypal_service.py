"""
Servicio PayPal real para procesamiento de pagos
Integración completa con PayPal REST API
"""
import requests
import json
from typing import Dict, Any, Optional
from app.core.config import settings


class PayPalService:
    """Servicio para integración con PayPal"""
    
    def __init__(self):
        self.client_id = settings.paypal_client_id
        self.client_secret = settings.paypal_client_secret
        self.mode = settings.paypal_mode
        self.base_url = settings.paypal_base_url
        self.return_url = settings.paypal_return_url
        self.cancel_url = settings.paypal_cancel_url
        self.access_token = None
        
        print(f"PayPal Service inicializado:")
        print(f"   Client ID: {'Configurado' if self.client_id else 'No configurado'}")
        print(f"   Client Secret: {'Configurado' if self.client_secret else 'No configurado'}")
        print(f"   Mode: {self.mode}")
        print(f"   Base URL: {self.base_url}")
    
    async def get_access_token(self) -> str:
        """Obtener token de acceso de PayPal"""
        if not self.client_id or not self.client_secret:
            raise ValueError("PayPal credentials not configured")
        
        url = f"{self.base_url}/v1/oauth2/token"
        
        headers = {
            "Accept": "application/json",
            "Accept-Language": "en_US",
        }
        
        data = {
            "grant_type": "client_credentials"
        }
        
        auth = (self.client_id, self.client_secret)
        
        try:
            response = requests.post(url, headers=headers, data=data, auth=auth)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data["access_token"]
            
            print(f"OK - PayPal access token obtenido (modo: {self.mode})")
            return self.access_token
            
        except requests.exceptions.RequestException as e:
            print(f"ERROR - Error obteniendo token PayPal: {e}")
            raise Exception(f"Error obteniendo token PayPal: {str(e)}")
    
    async def create_payment(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear pago en PayPal"""
        if not self.access_token:
            await self.get_access_token()
        
        url = f"{self.base_url}/v1/payments/payment"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Accept-Language": "en_US",
        }
        
        # Preparar datos del pago
        # Calcular total si no está presente o es 0
        if not order_data.get("total_amount") or float(order_data["total_amount"]) == 0:
            total_amount = sum(float(item["price"]) * int(item["quantity"]) for item in order_data["items"])
            order_data["total_amount"] = total_amount
        
        payment_data = {
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": self.return_url,
                "cancel_url": self.cancel_url
            },
            "transactions": [
                {
                    "amount": {
                        "total": f"{order_data['total_amount']:.2f}",
                        "currency": "USD"
                    },
                    "description": f"Pedido #{order_data['order_id']}",
                    "item_list": {
                        "items": [
                            {
                                "name": item["name"],
                                "sku": str(item.get("product_id", "")),
                                "price": f"{float(item['price']):.2f}",
                                "currency": "USD",
                                "quantity": str(item["quantity"])
                            }
                            for item in order_data["items"]
                        ]
                    }
                }
            ]
        }
        
        try:
            print(f"DEBUG Enviando pago a PayPal: {url}")
            print(f"DEBUG Headers: {headers}")
            print(f"DEBUG Payment data: {payment_data}")
            
            response = requests.post(url, headers=headers, json=payment_data)
            
            print(f"DEBUG Status code: {response.status_code}")
            print(f"DEBUG Response headers: {dict(response.headers)}")
            print(f"DEBUG Response text: {response.text}")
            
            response.raise_for_status()
            
            payment_response = response.json()
            print(f"DEBUG Payment response: {payment_response}")
            
            # Verificar que la respuesta tenga la estructura esperada
            if not payment_response:
                print(f"ERROR Respuesta PayPal vacía")
                raise Exception("Respuesta PayPal vacía")
            
            if "id" not in payment_response:
                print(f"ERROR Respuesta PayPal sin 'id': {payment_response}")
                print(f"ERROR Claves disponibles: {list(payment_response.keys())}")
                raise Exception(f"Respuesta PayPal inválida - falta 'id'. Claves: {list(payment_response.keys())}")
            
            print(f"OK Pago PayPal creado: {payment_response['id']}")
            return payment_response
            
        except requests.exceptions.RequestException as e:
            print(f"ERROR Error creando pago PayPal: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"ERROR Response status: {e.response.status_code}")
                print(f"ERROR Response headers: {dict(e.response.headers)}")
                print(f"ERROR Response text: {e.response.text}")
                try:
                    error_details = e.response.json()
                    print(f"ERROR Detalles del error PayPal: {error_details}")
                except:
                    print(f"ERROR No se pudo parsear error como JSON")
            raise Exception(f"Error creando pago PayPal: {str(e)}")
    
    async def execute_payment(self, payment_id: str, payer_id: str) -> Dict[str, Any]:
        """Ejecutar pago de PayPal"""
        if not self.access_token:
            await self.get_access_token()
        
        url = f"{self.base_url}/v1/payments/payment/{payment_id}/execute"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Accept-Language": "en_US",
        }
        
        data = {
            "payer_id": payer_id
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            execution_response = response.json()
            
            print(f"OK Pago PayPal ejecutado: {payment_id}")
            return execution_response
            
        except requests.exceptions.RequestException as e:
            print(f"ERROR Error ejecutando pago PayPal: {e}")
            raise Exception(f"Error ejecutando pago PayPal: {str(e)}")
    
    async def get_payment_details(self, payment_id: str) -> Dict[str, Any]:
        """Obtener detalles de un pago"""
        if not self.access_token:
            await self.get_access_token()
        
        url = f"{self.base_url}/v1/payments/payment/{payment_id}"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Accept-Language": "en_US",
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            payment_details = response.json()
            return payment_details
            
        except requests.exceptions.RequestException as e:
            print(f"ERROR Error obteniendo detalles PayPal: {e}")
            raise Exception(f"Error obteniendo detalles PayPal: {str(e)}")
    
    def get_approval_url(self, payment_response: Dict[str, Any]) -> Optional[str]:
        """Extraer URL de aprobación del pago"""
        try:
            links = payment_response.get("links", [])
            for link in links:
                if link.get("rel") == "approval_url":
                    return link.get("href")
            return None
        except Exception as e:
            print(f"ERROR Error extrayendo approval URL: {e}")
            return None
    
    def is_payment_completed(self, execution_response: Dict[str, Any]) -> bool:
        """Verificar si el pago fue completado exitosamente"""
        try:
            state = execution_response.get("state", "").lower()
            return state == "approved"
        except Exception:
            return False
    
    def get_transaction_id(self, execution_response: Dict[str, Any]) -> Optional[str]:
        """Obtener ID de transacción"""
        try:
            transactions = execution_response.get("transactions", [])
            if transactions:
                related_resources = transactions[0].get("related_resources", [])
                if related_resources:
                    sale = related_resources[0].get("sale", {})
                    return sale.get("id")
            return None
        except Exception:
            return None


# Instancia global del servicio
paypal_service = PayPalService()



