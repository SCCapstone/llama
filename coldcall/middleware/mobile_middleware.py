# middleware are called upon each request
def mobile_template_middleware(get_response):
    def middleware(request):
        request.is_mobile = "mobile" in request.META.get("HTTP_USER_AGENT", "").lower()

        response = get_response(request)
        return response
    return middleware