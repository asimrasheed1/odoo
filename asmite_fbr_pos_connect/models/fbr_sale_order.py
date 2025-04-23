import requests
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = 'pos.order'
    
    # x_fbr_inv = fields.Char(string="FBR Invoice")

    def action_pos_order_paid(self):
        _logger.info(" Checking if PoS order is a return or sale...")

        res = super(PosOrder, self).action_pos_order_paid()

        for order in self:
            _logger.info(f" Processing PoS Order: {order.name}, Amount Total: {order.amount_total}")

            # Check if it contains any negative lines → indicates a return
            is_return = any(line.qty < 0 for line in order.lines)

            invoice_type = "3" if is_return else "1"
            REFUSIN = str(order.id) if is_return else None

            url = "http://asmite.pk/baj/odoo/process_orders.php"
            # url = "https://textile.march7.group/fbr/odoo/process_orders.php"
            total_sales_value = 0
            total_tax_charged = 0
            total_quantity = 0
            total_bill_amount = 0
            total_discount = 0
            item_data = []
            for line in order.lines:
                product = line.product_id

                hs_code = product.hs_code if hasattr(product, 'hs_code') else "0000"
                tax_rate = 0.0
                tax_included = any(tax.price_include_override for tax in line.tax_ids_after_fiscal_position)
                _logger.info(f" PoS tax_included {tax_included}.")

                for tax in line.tax_ids_after_fiscal_position:
                    tax_rate += tax.amount
                    
                # if(tax_included == 'tax_excluded'):
                #     sales_value = (line.price_subtotal_incl * 100) / (100 + tax_rate)
                #     tax_charged = sales_value - tax_rate
                #     totalamount = sales_value + tax_rate
                # else:
                sales_value = line.price_subtotal
                tax_charged = line.price_subtotal_incl - line.price_subtotal
                totalamount = line.price_subtotal_incl
                total_sales_value += sales_value
                total_tax_charged += tax_charged
                total_quantity += (line.qty)
                total_bill_amount += (totalamount)

                data = {
                    "ItemCode": product.default_code or str(product.id),
                    "ItemName": product.name,
                    "Quantity": line.qty,
                    "PCTCode": hs_code,
                    "TaxRate": str(tax_rate),
                    "SaleValue": sales_value,
                    "TotalAmount": sales_value,
                    "TaxCharged": tax_charged,
                    "Discount": 0,
                    "FurtherTax": 0,
                    "InvoiceType": invoice_type,
                    "RefUSIN": REFUSIN
                }
                item_data.append(data)                
            order_data = {
                "InvoiceNumber": "",
                "POSID": order.config_id.name or "Unknown POS",
                "USIN": str(order.id),
                "DateTime": order.date_order.strftime("%Y-%m-%d %H:%M:%S"),
                "BuyerNTN": "",
                "BuyerCNIC": "",
                "BuyerName": order.partner_id.name or "",
                "BuyerPhoneNumber": order.partner_id.phone or "",
                "TotalBillAmount": abs(total_bill_amount),
                "TotalQuantity": abs(total_quantity),
                "TotalSaleValue": abs(total_sales_value),
                "TotalTaxCharged": abs(total_tax_charged),
                "Discount": 0,
                "FurtherTax": 0,
                "PaymentMode": "1",
                "RefUSIN": REFUSIN,
                "InvoiceType": invoice_type,
                "Items": item_data,
            }
            try:
                _logger.info(" Sending FBR PoS Order Data: %s", order_data)
                response = requests.post(url, json=order_data, timeout=10)

                if response.status_code == 200:
                    _logger.info(f" PoS Order {order.name} sent successfully to FBR.")
                    _logger.info(f"FBR Response: {response.text}")
                    order.x_fbr_inv = response.text
                else:
                    _logger.error(f" Failed to send PoS order {order.name}. Status: {response.status_code} Response: {response.text}")
            except requests.exceptions.RequestException as e:
                _logger.error(f" Error sending PoS order {order.name}: {e}")

        return res
