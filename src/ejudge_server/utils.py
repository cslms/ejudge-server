def get_request_args(request, *args, **kwargs):
    """
    Return a dictionary of arguments from request data.

    The name of the desired arguments must be passed as positional arguments.
    Keyword arguments provide argument names with their respective default
    values.
    """

    data = request.data
    result = {}

    if request.content_type in ('application/json', 'x-www-form-urlencoded'):
        for arg in args:
            try:
                result[arg] = data[arg]
            except KeyError:
                raise ValueError('%r key not found in data' % arg)
        for arg, default in kwargs.items():
            result[arg] = data.get(arg)
    else:
        raise ValueError('unssuported data: %s' % request.content_type)
    return result