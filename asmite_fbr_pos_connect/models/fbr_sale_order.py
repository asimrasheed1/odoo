import requests
from odoo import models, fields, api
class PosOrder(models.Model):
    _inherit = 'pos.order'
    def action_pos_order_paid(self):
        res = super(PosOrder, self).action_pos_order_paid()
        for order in self:
# Check if it contains any negative lines → indicates a return
            is_return = any(line.qty < 0 for line in order.lines)
            invoice_type = "3" if is_return else "1"
            REFUSIN = str(order.id) if is_return else None
            url = "https://asmite.pk/baj/odoo/process_orders.php"
            total_sales_value = 0
            total_tax_charged = 0
            total_quantity = 0
            total_bill_amount = 0
            total_discount = 0
            item_data = []
            for line in order.lines:
                product = line.product_id
                hs_code = product.hs_code if hasattr(product, 'hs_code') else ""
                tax_rate = 0.0
                for tax in line.tax_ids_after_fiscal_position:
                    tax_rate += tax.amount
                sales_value = line.price_subtotal
                tax_charged = line.price_subtotal_incl - line.price_subtotal
                total_amount = line.price_subtotal_incl
                total_sales_value += sales_value
                total_tax_charged += tax_charged
                total_quantity += (line.qty)
                total_bill_amount += (total_amount)
                data = {
                    "ItemCode": product.id,
                    "ItemName": product.name,
                    "Quantity": line.qty,
                    "PCTCode": hs_code,
                    "TaxRate": str(tax_rate),
                    "SaleValue": sales_value,
                    "TotalAmount": total_amount,
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
            response = requests.post(url, json=order_data, timeout=10)
            if response.status_code == 200:
              order.x_fbr_inv = response.text
        return res
