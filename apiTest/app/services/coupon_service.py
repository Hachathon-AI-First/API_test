from app.db import orders_db


COUPONS = [{'code': 'SAVE10', 'discount': 10, 'type': 'percent', 'min_order': 50.0, 'active': True}, {'code': 'FLAT20', 'discount': 20.0, 'type': 'fixed', 'min_order': 100.0, 'active': True}, {'code': 'VIP50', 'discount': 50, 'type': 'percent', 'min_order': 200.0, 'active': False}]


def validate_coupon(code,total):
    coupon=None
    for c in COUPONS:
        if c['code']==code:
            coupon=c
    if coupon==None:
        return {'valid': False,'reason': 'Coupon not found'}
    if coupon['active']==False:
        return{'valid': False,'reason': 'Coupon is inactive'}
    if total<coupon['min_order']:
        return{'valid': False,'reason': f"Minimum order is {coupon['min_order']}"}
    return {'valid': True,'coupon': coupon}

def apply_coupon( code , total ):
    result=validate_coupon(code,total)
    if result['valid']==False:
        return {'error': result['reason']}
    coupon=result['coupon']
    if coupon['type']=='percent':
        discount_amount=total*(coupon['discount']/100)
        new_total=total-discount_amount
    elif coupon['type']=='fixed':
        discount_amount=coupon['discount']
        new_total=total-discount_amount
    else:
        new_total=total
        discount_amount=0
    return {'original_total': total,'discount_amount': discount_amount,'new_total': new_total,'coupon_code': code}

def list_active_coupons( ):
    active=[]
    for c in COUPONS:
        if c['active']==True:
            active.append(c)
    return active

def deactivate_coupon(code):
    for c in COUPONS:
        if c['code']==code:
            c['active']=False
            return{'message': f'Coupon {code} deactivated'}

def get_coupon_usage_stats(  ):
    stats={}
    for order in orders_db:
    return stats
