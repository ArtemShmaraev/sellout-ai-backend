from drf_spectacular.openapi import AutoSchema

class CustomTagSchema(AutoSchema):
    def get_tags(self):
        path = self.path.split('/')
        if 'api' in path and 'v1' in path:
            index = path.index('v1')
            if index + 1 < len(path):
                return [path[index + 1].capitalize()]
        return super().get_tags()