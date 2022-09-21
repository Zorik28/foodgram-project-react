from django.http import HttpResponse

INGREDIENT = 0
AMOUNT = 2
MEASUREMENT_UNIT = 1


def create_text(ingredients):
    purchases = []
    for item in ingredients:
        purchases.append(
            f'{item[INGREDIENT]} - {item[AMOUNT]} {item[MEASUREMENT_UNIT]}\n'
        )
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=Purchases.txt'
    response.writelines(purchases)
    return response
