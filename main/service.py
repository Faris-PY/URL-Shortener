import random
import string
from django.urls import reverse
from account.models import Urls


def randomHashValue(id, rangeValue):
    random_hash = str(id) + ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(rangeValue))   
    return random_hash

def shorten(request, url, irterate=7):
    
    oldUrl = url
    random_hash = randomHashValue(request.user.pk, irterate)
    new_temp_url = request.build_absolute_uri(reverse('redirect', args=[random_hash]))
    
    if not Urls.objects.filter(new_url=new_temp_url, user_id=request.user.pk).exists():
        url = Urls(user=request.user, old_url=url, new_url=new_temp_url)
        url.save()
        return True
    else:
        irterate += 1 
        return shorten(request, oldUrl, irterate) 
 
def load_url(request, url):

    new_temp_url = request.build_absolute_uri(reverse('redirect', args=[url]))
    try:
        resultSet =  Urls.objects.get(new_url=new_temp_url, is_active = True)
        original_url = resultSet.old_url
    except Urls.DoesNotExist:
        return None
    return original_url

