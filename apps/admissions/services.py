from django.db.models import Sum

from .models import Payment
from .models import Student


def get_fee_summary():

    # TOTAL COLLECTED
    total_collected = Payment.objects.filter(
        status='SUCCESS'
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0

    # TOTAL OUTSTANDING
    total_outstanding = 0

    for student in Student.objects.all():

        total_outstanding += student.pending_amount()

    # TOTAL RECEIPTS
    total_receipts = Payment.objects.count()

    return {
        'collected': total_collected,
        'outstanding': total_outstanding,
        'receipts': total_receipts
    }
    
    