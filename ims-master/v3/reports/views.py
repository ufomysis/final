from django.shortcuts import render
from items.models import Item
from django.utils import timezone
from utils.decorators import inv_manager_ad_required_fbv


@inv_manager_ad_required_fbv
def CurrentStockBranchReport(request):
    if request.user.user_type == 'administrator':
        branch = None
        infos = Item.objects.filter(status='info').order_by('currently_at')
    else:
        branch = request.user.branch

        infos = Item.objects.filter(status='info', currently_at=branch).order_by('item_abstract__title')

    q_infos = {}
    for id, item in enumerate(infos):
        q_infos[id] = {
            'instance': item,
            'q': item.get_q_this_branch(),
        }



    context = {
        'q':q_infos,
        'branch': branch,
        'date': timezone.now()
    }
    return render(request, "reports/c_stock_.html", context)



