from Views.Widgets import PlaybookWidget
from services.Local_DB.DTO.output_DTO import PlaybookOutDTO
from services.common.base_mapper import BaseMapper


class PlaybookMapperAPI(BaseMapper[PlaybookWidget, PlaybookOutDTO]):

    @classmethod
    def _dto_to_app_obj(cls, playbook: 'PlaybookOutDTO') -> 'PlaybookWidget':
        pass