import json
from json.decoder import JSONDecodeError
from django.http.request import RawPostDataException
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

from utils import Snake, Hump


class ArgumentNamingRuleMiddleware(MiddlewareMixin):
    def __init__(self, *args, **kwargs):
        super(ArgumentNamingRuleMiddleware, self).__init__(*args, **kwargs)
        try:
            params_loads = settings.MICRO_PARAMS_LOADS
        except AttributeError:
            params_loads = False
        self.snake = Snake(loads=params_loads)
        self.hump = Hump()
        self.allowed_method = ['GET', 'POST', 'PUT', 'DELETE']

    def process_request(self, request):
        if request.method in self.allowed_method:
            # request.GET
            _get = request.GET.copy()
            get_data = self.snake.to_snake(_get)
            request.GET = get_data

            # request.POST
            _post = request.POST.copy()
            post_data = self.snake.to_snake(_post)
            request.POST = post_data

            # request.body
            try:
                _body = json.loads(request.body.decode('utf-8'))
                body_data = self.snake.to_snake(_body)
                request._body = json.dumps(body_data).encode('utf-8')
            except (JSONDecodeError, AttributeError, RawPostDataException,
                    UnicodeDecodeError, UnicodeEncodeError):
                pass

            # request.FILES
            _files = request.FILES.copy()
            file_data = self.snake.to_snake(_files)
            request._files = file_data
        return None

    def process_response(self, request, response):
        if response.status_code == 200:
            try:
                response_data = self.hump.to_hump(response.data.get('data'))
                response.data['data'] = response_data
                response.render()
            except:
                pass
        return response
