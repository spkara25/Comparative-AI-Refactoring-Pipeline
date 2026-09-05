def calculate_shipping(weight, destination, member_status, coupon=None):
    cost = 0
    if weight <= 0:
        return 0
    
    if destination == "DOMESTIC":
        if member_status == "PLATINUM":
            cost = 5.0
        elif member_status == "GOLD":
            if weight > 10:
                cost = 10.0 + (weight - 10) * 1.5
            else:
                cost = 10.0
        else:
            if weight > 20:
                cost = 25.0
            elif weight > 10:
                cost = 15.0
            else:
                cost = 8.0
    elif destination == "INTERNATIONAL":
        if member_status == "PLATINUM":
            cost = 20.0 + weight * 2.0
        else:
            if weight > 15:
                cost = 45.0 + weight * 3.5
            else:
                cost = 30.0 + weight * 2.5
    else:
        return -1

    if coupon:
        if coupon == "HALF":
            cost = cost * 0.5
        elif coupon == "MINUS5":
            cost = max(0, cost - 5.0)

    return round(cost, 2)