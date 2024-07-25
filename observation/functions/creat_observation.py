from observation.models import ObservationInfo, ObservationOptions
from .infos import infos, options


def creat_observation_info():
    for info in infos:
        ObservationInfo.objects.get_or_create(
            title=info['title']
        )
    return True


def creat_observation_options():
    for option in options:
        ObservationOptions.objects.get_or_create(
            name=option['name'],
            value=option['value']
        )
    return True
