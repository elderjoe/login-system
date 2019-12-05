def client_ip(request):
    """
    Get clients IP address
    :Parameters:
        request: (obj)
    :Returns:
       ip: (str) IP Address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if request.META.get('HTTP_X_REAL_IP'):
        ip = request.META.get('HTTP_X_REAL_IP')
    elif x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
