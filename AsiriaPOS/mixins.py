from drf_yasg.utils import swagger_auto_schema
from functools import wraps

class SwaggerTagMixin:
    swagger_tag = None  # Set in your ViewSet

    @classmethod
    def as_view(cls, actions=None, **initkwargs):
        view = super().as_view(actions, **initkwargs)
        
        if cls.swagger_tag:
            for method_name in ['get', 'post', 'put', 'patch', 'delete']:
                if hasattr(view.cls, method_name):
                    original_method = getattr(view.cls, method_name)
                    decorated = swagger_auto_schema(tags=[cls.swagger_tag])(original_method)
                    setattr(view.cls, method_name, decorated)
        
        return view
