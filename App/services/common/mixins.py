from pydantic import field_validator, model_validator

from services.common.validators import validate_x, validate_y, validate_right_border, validate_bot_border


class ValidatePointCoordinatesMixin:
    @field_validator('x', mode='after')
    def validate_x(cls, value, info):
        if info.context and 'playbook_type' in info.context:
            playbook_type = info.context['playbook_type']
            validate_x(value, playbook_type)
        return value

    @field_validator('y', mode='after')
    def validate_y(cls, value, info):
        if info.context and 'playbook_type' in info.context:
            playbook_type = info.context['playbook_type']
            validate_y(value, playbook_type)
        return value


class ValidateLineCoordinatesMixin:
    @field_validator('x1', mode='after')
    def validate_x1(cls, value, info):
        if info.context and 'playbook_type' in info.context:
            playbook_type = info.context['playbook_type']
            validate_x(value, playbook_type)
        return value

    @field_validator('y1', mode='after')
    def validate_y1(cls, value, info):
        if info.context and 'playbook_type' in info.context:
            playbook_type = info.context['playbook_type']
            validate_y(value, playbook_type)
        return value

    @field_validator('x2', mode='after')
    def validate_x2(cls, value, info):
        if info.context and 'playbook_type' in info.context:
            playbook_type = info.context['playbook_type']
            validate_x(value, playbook_type)
        return value

    @field_validator('y2', mode='after')
    def validate_y2(cls, value, info):
        if info.context and 'playbook_type' in info.context:
            playbook_type = info.context['playbook_type']
            validate_y(value, playbook_type)
        return value


class ValidateWidthAndHeightMixin:
    @model_validator(mode='after')
    def validate_width(self, info):
        if info.context and 'playbook_type' in info.context:
            playbook_type = info.context['playbook_type']
            validate_right_border(self.x, self.width, playbook_type)
        return self

    @model_validator(mode='after')
    def validate_height(self, info):
        if info.context and 'playbook_type' in info.context:
            playbook_type = info.context['playbook_type']
            validate_bot_border(self.y, self.height, playbook_type)
        return self

