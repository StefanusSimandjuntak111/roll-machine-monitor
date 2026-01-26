"""
ERP Client for Frappe/ERPNext integration.

This module handles authentication and API communication with ERPNext
for submitting Stock Entry documents from batch production data.
"""
import requests
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json
import os
import sys

logger = logging.getLogger(__name__)


class ERPClient:
    """Client for communicating with Frappe/ERPNext API."""
    
    def __init__(
        self,
        base_url: str,
        api_key: str,
        api_secret: str,
        timeout: int = 30
    ):
        """
        Initialize ERP client.
        
        Args:
            base_url: Base URL of ERPNext instance (e.g., http://192.168.1.100:8000)
            api_key: API key for authentication
            api_secret: API secret for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.api_secret = api_secret
        self.timeout = timeout
        self.session = requests.Session()
        
        # Set authentication headers
        self.session.headers.update({
            'Authorization': f'token {api_key}:{api_secret}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        logger.info(f"ERP Client initialized for {self.base_url}")
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        Test connection to ERP system.
        
        Returns:
            Tuple of (success, message)
        """
        try:
            url = f"{self.base_url}/api/method/frappe.auth.get_logged_user"
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                user = data.get('message', 'Unknown')
                logger.info(f"ERP connection successful. Authenticated as: {user}")
                return True, f"Terhubung sebagai {user}"
            else:
                logger.error(f"Connection failed: HTTP {response.status_code}")
                return False, "Koneksi gagal, periksa URL dan API key"
                
        except requests.exceptions.Timeout:
            logger.error("Connection timeout")
            return False, "Koneksi timeout"
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {str(e)}")
            return False, "Tidak dapat terhubung ke server ERP"
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return False, "Terjadi kesalahan saat menghubungi server"
    
    def get_bom_items(self, bom_name: str) -> Tuple[bool, List[Dict[str, Any]], str]:
        """
        Get BOM items from ERPNext.
        
        Args:
            bom_name: BOM name/ID in ERPNext
            
        Returns:
            Tuple of (success, items_list, error_message)
        """
        try:
            url = f"{self.base_url}/api/resource/BOM/{bom_name}"
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                bom_data = response.json().get('data', {})
                items = bom_data.get('items', [])
                logger.info(f"Retrieved {len(items)} items from BOM: {bom_name}")
                return True, items, ""
            else:
                logger.error(f"Failed to get BOM: HTTP {response.status_code}")
                return False, [], f"BOM '{bom_name}' tidak ditemukan"
                
        except Exception as e:
            logger.error(f"Error fetching BOM: {str(e)}")
            return False, [], f"Gagal mengambil data BOM: {str(e)}"
    
    def create_stock_entry(
        self,
        batch_data: Dict[str, Any],
        company: str = "Textilindo",
        from_warehouse: str = "Prancis - MGI",
        to_warehouse: str = "Prancis - MGI",
        bom_name: Optional[str] = None,
        finished_item_code: Optional[str] = None,
        stock_entry_type: str = "Repack"
    ) -> Tuple[bool, str, Optional[Dict]]:
        """
        Create Stock Entry document in ERP from batch data.
        
        Args:
            batch_data: Batch summary data with logs
            company: Company name in ERP
            from_warehouse: Source warehouse
            to_warehouse: Target warehouse
            
        Returns:
            Tuple of (success, message, response_data)
        """
        try:
            # Get packing list field name from config (if available)
            try:
                from monitoring.config import load_config
                config = load_config()
                packing_list_field = config.get('erp_packing_list_field', 'packing_list_items')
            except ImportError:
                # Fallback if import fails
                packing_list_field = 'packing_list_items'
                logger.warning("Could not import config, using default packing_list_items")
            
            # Get BOM items if BOM is provided
            bom_items = []
            if bom_name:
                logger.info(f"Fetching BOM items from: {bom_name}")
                success, bom_items, error_msg = self.get_bom_items(bom_name)
                if not success:
                    return False, f"Failed to fetch BOM: {error_msg}", None
                logger.info(f"Retrieved {len(bom_items)} items from BOM")
            
            # Prepare Stock Entry document
            stock_entry_doc = self._prepare_stock_entry(
                batch_data=batch_data,
                company=company,
                from_warehouse=from_warehouse,
                to_warehouse=to_warehouse,
                bom_items=bom_items,
                finished_item_code=finished_item_code,
                packing_list_field=packing_list_field,
                stock_entry_type=stock_entry_type
            )
            
            # Log the prepared document for debugging (summary only to avoid huge logs)
            logger.info(f"Prepared Stock Entry - Batch: {batch_data.get('batch')}, Items: {len(stock_entry_doc.get('items', []))}, Packing List: {len(stock_entry_doc.get('packing_list', []))}")
            logger.debug(f"Full Stock Entry document: {json.dumps(stock_entry_doc, indent=2)}")
            
            # Submit to ERP
            url = f"{self.base_url}/api/resource/Stock Entry"
            logger.info(f"Submitting Stock Entry to: {url}")
            logger.info(f"Authentication: token {self.api_key[:10]}...:{self.api_secret[:5]}...")
            
            response = self.session.post(
                url,
                json=stock_entry_doc,
                timeout=self.timeout
            )
            
            logger.info(f"Response status code: {response.status_code}")
            logger.info(f"Response headers: {dict(response.headers)}")
            logger.info(f"Response content length: {len(response.content)} bytes")
            
            if response.status_code in [200, 201]:
                try:
                    response_data = response.json()
                    doc_name = response_data.get('data', {}).get('name', 'Unknown')
                    success_msg = f"Stock Entry created successfully: {doc_name}"
                    logger.info(success_msg)
                    return True, success_msg, response_data
                except ValueError as json_err:
                    logger.error(f"Failed to parse success response as JSON: {json_err}")
                    logger.error(f"Response content: {response.text[:500]}")
                    return False, "Server returned invalid response format", None
            else:
                # Log response for debugging (full detail with HTTP code)
                logger.error(f"HTTP {response.status_code} response: {response.text[:500]}")
                
                try:
                    error_data = response.json() if response.content else {}
                    # Extract error message from response (without HTTP code in user-facing message)
                    raw_error = error_data.get('exception') or error_data.get('message') or error_data.get('exc') or ''
                    
                    # Clean up error message for display
                    if raw_error:
                        # Remove technical traceback if present
                        if 'Traceback' in raw_error:
                            # Extract just the last line (the actual error message)
                            error_lines = raw_error.split('\n')
                            # Get the last non-empty line
                            for line in reversed(error_lines):
                                if line.strip():
                                    error_msg = line.strip()
                                    break
                            else:
                                error_msg = "Server error occurred"
                        else:
                            error_msg = raw_error
                    else:
                        # No error message from server
                        error_msg = "Server error occurred"
                    
                except ValueError:
                    # Response is not JSON
                    logger.error(f"Non-JSON error response - HTTP {response.status_code}: {response.text[:200]}")
                    # Extract text content if available, otherwise generic message
                    if response.text:
                        # Check if it's HTML error page
                        if response.text.strip().lower().startswith(('<!doctype', '<html', '<title>')):
                            # Try to extract error from <title> tag
                            import re
                            title_match = re.search(r'<title>([^<]+)</title>', response.text, re.IGNORECASE)
                            if title_match:
                                error_title = title_match.group(1)
                                # Remove "// Werkzeug Debugger" or similar suffixes
                                error_msg = re.sub(r'\s*//.*$', '', error_title).strip()
                            else:
                                error_msg = "Server mengalami internal error"
                        else:
                            # Plain text error
                            error_msg = response.text[:200].strip()
                    else:
                        error_msg = "Server mengembalikan response kosong"
                    error_data = None
                
                # Log full error for debugging
                logger.error(f"Failed to create Stock Entry: {error_msg}")
                
                # Return user-friendly error without HTTP code
                return False, f"ERP Error: {error_msg}", error_data
                
        except requests.exceptions.Timeout:
            error_msg = "ERP server tidak merespon (timeout)"
            logger.error(f"Request timeout - ERP server not responding")
            return False, error_msg, None
        except requests.exceptions.ConnectionError as e:
            error_msg = "Tidak dapat terhubung ke ERP server"
            logger.error(f"Connection error: {str(e)}")
            return False, error_msg, None
        except ValueError as ve:
            # Validation errors from _prepare_stock_entry
            error_msg = str(ve)
            logger.error(f"Validation error: {error_msg}")
            return False, error_msg, None
        except Exception as e:
            error_msg = f"Terjadi kesalahan: {str(e)}"
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return False, error_msg, None
    
    def _prepare_stock_entry(
        self,
        batch_data: Dict[str, Any],
        company: str,
        from_warehouse: str,
        to_warehouse: str,
        bom_items: List[Dict[str, Any]] = None,
        finished_item_code: Optional[str] = None,
        packing_list_field: str = "packing_list_items",
        stock_entry_type: str = "Repack"
    ) -> Dict[str, Any]:
        """
        Prepare Stock Entry document from batch data.
        
        For Repack Stock Entry:
        - Source items (raw materials from BOM) go to s_warehouse
        - Finished items (finished goods) come from t_warehouse
        
        Args:
            batch_data: Batch summary with logs
            company: Company name
            from_warehouse: Source warehouse
            to_warehouse: Target warehouse
            bom_items: Items from BOM (raw materials)
            finished_item_code: Finished item code (what's being produced)
            
        Returns:
            Stock Entry document dict
        """
        logs = batch_data.get('logs', [])
        batch_number = batch_data.get('batch', '')
        product_code = batch_data.get('product_code', '')
        
        # Use provided finished item or fall back to product_code
        finished_item = finished_item_code or product_code
        
        # Use BOM items if provided
        if bom_items is None:
            bom_items = []
        
        # Prepare packing list items
        packing_list = []
        total_qty = 0.0
        
        # Validate we have logs
        if not logs:
            logger.error("No logs found in batch data")
            raise ValueError("Batch data contains no production logs")
        
        logger.info(f"Processing {len(logs)} logs for batch {batch_number}")
        logger.info(f"BOM Items Count: {len(bom_items) if bom_items else 0}")
        logger.info(f"Finished Item (Product): {finished_item}")
        
        for i, log in enumerate(logs):
            item_code = log.get('product_code', product_code)
            length = log.get('product_length', 0)
            roll_number = i + 1
            
            # Skip entries with invalid length
            if not length or length <= 0:
                logger.warning(f"Skipping roll {roll_number}: invalid length {length}")
                continue
            
            total_qty += float(length)
            
            # Generate barcode_id from batch and roll number
            barcode_id = f"{finished_item}-{length}"
            
            # Packing list entry (individual finished roll)
            # Fields match ERPNext custom child table: item_code, roll_qty, weight__length, barcode_id
            packing_list.append({
                'item_code': finished_item,
                'roll_qty': 1,
                'weight__length': float(length),  # Note: double underscore!
                'barcode_id': barcode_id
            })
        
        # Validate we have valid quantity
        if total_qty <= 0:
            logger.error("No valid items to submit - all rolls have invalid length")
            raise ValueError("No valid production data found in batch (all lengths are 0 or invalid)")
        
        # Create Stock Entry items from BOM
        items = []
        
        # Add source items from BOM (raw materials being consumed)
        if bom_items:
            logger.info(f"Adding {len(bom_items)} source items from BOM")
            for bom_item in bom_items:
                item_code = bom_item.get('item_code')
                bom_qty = bom_item.get('qty', 0)
                uom = bom_item.get('uom', 'Yard')
                
                # Validate item_code exists
                if not item_code:
                    logger.error(f"BOM item has no item_code: {bom_item}")
                    raise ValueError(f"BOM item missing item_code")
                
                # Calculate actual qty based on batch total_qty
                # BOM qty is per unit, multiply by total production qty
                actual_qty = float(bom_qty) * total_qty
                
                items.append({
                    'item_code': item_code,
                    'qty': actual_qty,
                    's_warehouse': from_warehouse,  # Source warehouse for raw materials
                    'uom': uom
                })
                logger.info(f"BOM Item: {item_code}, BOM qty: {bom_qty}, Actual qty: {actual_qty:.2f} {uom}")
        
        # Validate finished item code
        if not finished_item:
            logger.error(f"Finished item code is empty! Product code: {product_code}, Finished item code: {finished_item_code}")
            raise ValueError("Finished item code cannot be empty")
        
        # Add finished item (finished good being produced)
        items.append({
            'item_code': finished_item,
            'qty': total_qty,
            't_warehouse': to_warehouse,  # Only target warehouse
            'uom': 'Yard'
        })
        
        logger.info(f"Finished item: {finished_item}, qty: {total_qty:.2f} yards (to {to_warehouse})")
        logger.info(f"Total items in Stock Entry: {len(items)} (Source: {len(bom_items) if bom_items else 0}, Finished: 1)")
        
        # Validate warehouses
        if not from_warehouse or not to_warehouse:
            logger.error(f"Warehouse validation failed - From: '{from_warehouse}', To: '{to_warehouse}'")
            raise ValueError("Both from_warehouse and to_warehouse must be specified")
        
        # Validate company
        if not company:
            logger.error("Company name is empty")
            raise ValueError("Company name must be specified")
        
        # Create Stock Entry document
        stock_entry = {
            'doctype': 'Stock Entry',
            'stock_entry_type': stock_entry_type,
            'purpose': stock_entry_type,
            'company': company,
            'posting_date': datetime.now().strftime('%Y-%m-%d'),
            'posting_time': datetime.now().strftime('%H:%M:%S'),
            'from_warehouse': from_warehouse,
            'to_warehouse': to_warehouse,
            'remarks': f"Batch {batch_number} - {batch_data.get('product_name', '')} - Auto-generated from Roll Machine Monitor",
            'items': items
        }
        
        logger.info(f"Stock Entry header: Company={company}, Type={stock_entry_type}, From={from_warehouse}, To={to_warehouse}")
        
        # IMPORTANT: packing_list is REQUIRED for Repack operations
        if not packing_list:
            logger.error("No packing list entries - but they are REQUIRED for Repack!")
            raise ValueError("Packing list items are required for Repack Stock Entry")
        
        # Add packing list using configured field name
        stock_entry[packing_list_field] = packing_list
        
        logger.info(f"Added {len(packing_list)} packing list entries to Stock Entry")
        logger.info(f"Packing list field name: '{packing_list_field}'")
        logger.info(f"Packing list sample (first item): {json.dumps(packing_list[0] if packing_list else None, indent=2)}")
        logger.info(f"Prepared Stock Entry: Type={stock_entry['stock_entry_type']}, Purpose={stock_entry['purpose']}, Items={len(items)}, Packing List={len(packing_list)} (from config)")
        
        # Log full document for debugging
        logger.info(f"Full Stock Entry document being sent:")
        logger.info(json.dumps(stock_entry, indent=2, default=str))
        
        return stock_entry
    
    def submit_document(self, doctype: str, docname: str) -> Tuple[bool, str]:
        """
        Submit a draft document in ERP.
        
        Args:
            doctype: Document type (e.g., 'Stock Entry')
            docname: Document name/ID
            
        Returns:
            Tuple of (success, message)
        """
        try:
            url = f"{self.base_url}/api/method/frappe.client.submit"
            payload = {
                'doc': json.dumps({
                    'doctype': doctype,
                    'name': docname
                })
            }
            
            response = self.session.post(url, json=payload, timeout=self.timeout)
            
            if response.status_code == 200:
                logger.info(f"Document {docname} submitted successfully")
                return True, f"Dokumen {docname} berhasil disubmit"
            else:
                logger.error(f"Submit failed: HTTP {response.status_code}")
                return False, "Gagal submit dokumen"
                
        except Exception as e:
            logger.error(f"Error submitting document: {str(e)}")
            return False, f"Gagal submit dokumen: {str(e)}"
    
    def close(self):
        """Close the session."""
        self.session.close()
        logger.info("ERP Client session closed")


def get_erp_client(config: Dict[str, Any]) -> Optional[ERPClient]:
    """
    Factory function to create ERP client from configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        ERPClient instance or None if not configured
    """
    erp_url = config.get('erp_url', '').strip()
    erp_api_key = config.get('erp_api_key', '').strip()
    erp_api_secret = config.get('erp_api_secret', '').strip()
    
    if not all([erp_url, erp_api_key, erp_api_secret]):
        logger.warning("ERP configuration incomplete - client not initialized")
        return None
    
    timeout = config.get('erp_timeout', 30)
    
    try:
        client = ERPClient(
            base_url=erp_url,
            api_key=erp_api_key,
            api_secret=erp_api_secret,
            timeout=timeout
        )
        return client
    except Exception as e:
        logger.error(f"Failed to create ERP client: {e}")
        return None

