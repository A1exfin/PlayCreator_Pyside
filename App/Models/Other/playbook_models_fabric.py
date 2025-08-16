from typing import TYPE_CHECKING, Optional
from uuid import UUID

import Config
from Config.Enums import PlaybookType, TeamType

from ..scheme_model import SchemeModel
from ..figure_model import FigureModel
from ..label_model import LabelModel
from ..pencil_line_model import PencilLineModel
from ..player_model import PlayerModel
from ..action_model import ActionModel
from ..action_line_model import ActionLineModel
from ..final_action_model import FinalActionModel


if TYPE_CHECKING:
    from ..playbook_model import PlaybookModel
    from Config.Enums import FigureType, PlayerPositionType, FillType, SymbolType,\
        ActionLineType, FinalActionType

__all__ = ('PlaybookModelsFabric',)


class PlaybookModelsFabric:
    def __init__(self, playbook_model: 'PlaybookModel'):
        self._playbook_model = playbook_model

    @property
    def playbook(self) -> 'PlaybookModel':
        return self._playbook_model

    def create_scheme_model(self, parent: 'PlaybookModel', name: str, view_point_x: int, view_point_y: int, note: str = '', zoom: int = 60,
                            first_team: Optional['TeamType'] = None, second_team: Optional['TeamType'] = None,
                            first_team_position: Optional[int] = None, uuid: Optional['UUID'] = None,
                            id_local_db: Optional[int] = None, id_api: Optional[int] = None) -> 'SchemeModel':
        return SchemeModel(self._playbook_model, name, view_point_x, view_point_y, note, zoom, first_team,
                           second_team, first_team_position, uuid, id_local_db, id_api, parent=parent)

    def create_figure_model(self, parent: 'SchemeModel', figure_type: 'FigureType', x: float, y: float,
                            width: float, height: float,
                            border: bool, border_thickness: int, border_color: str,
                            fill: bool, fill_opacity: str, fill_color: str,
                            uuid: Optional['UUID'] = None,
                            id_local_db: Optional[int] = None, id_api: Optional[int] = None) -> 'FigureModel':
        return FigureModel(self._playbook_model, figure_type, x, y, width, height,
                           border, border_thickness, border_color,
                           fill, fill_opacity, fill_color,
                           uuid, id_local_db, id_api, parent=parent)

    def create_label_model(self, parent: 'SchemeModel', x: float, y: float, width: float, height: float,
                           text: str, font_type: str, font_size: int,
                           font_bold: bool, font_italic: bool, font_underline: bool, font_color: str,
                           uuid: Optional['UUID'] = None,
                           id_local_db: Optional[int] = None, id_api: Optional[int] = None) -> 'LabelModel':
        return LabelModel(self._playbook_model, x, y, width, height, text, font_type, font_size,
                          font_bold, font_italic, font_underline, font_color, uuid, id_local_db, id_api, parent=parent)

    def create_pencil_line_model(self, parent: 'SchemeModel', x1: float, y1: float, x2: float, y2: float,
                                 thickness: int, color: str,
                                 uuid: Optional['UUID'] = None,
                                 id_local_db: Optional[int] = None, id_api: Optional[int] = None,) -> 'PencilLineModel':
        return PencilLineModel(self._playbook_model, x1, y1, x2, y2, thickness, color, uuid, id_local_db, id_api, parent=parent)

    def create_new_first_team_player_models(self, parent: 'SchemeModel', team_type: 'TeamType',
                                            first_team_position: int) -> list['PlayerModel']:
        player_models_lst = []
        playbook_type = self._playbook_model.playbook_type
        yards_to_top_border = self._get_yards_to_top_field_border(playbook_type, first_team_position)
        vertical_one_yard = getattr(Config, f'{playbook_type.name}_field_data'.lower()).vertical_one_yard
        players_data = getattr(getattr(Config, f'{playbook_type.name.lower()}_players_data'), f'{team_type.name.lower()}')
        for i, player_data in enumerate(players_data):
            team_type, position, text, fill_type, x, y = player_data
            if team_type is TeamType.PUNT and i == 10 and yards_to_top_border >= 105 * vertical_one_yard:
                player_model = PlayerModel(self._playbook_model, team_type, position, text, x,
                                           118 * vertical_one_yard, fill_type=fill_type, parent=parent)
            else:
                player_model = PlayerModel(self._playbook_model, team_type, position, text, x,
                                           y + yards_to_top_border, fill_type=fill_type, parent=parent)
            player_models_lst.append(player_model)
        return player_models_lst

    def create_new_second_team_player_models(self, parent: 'SchemeModel', team_type: 'TeamType', first_team_position: int) -> list['PlayerModel']:
        player_models_lst = []
        playbook_type = self._playbook_model.playbook_type
        yards_to_top_border = self._get_yards_to_top_field_border(playbook_type, first_team_position)
        vertical_one_yard = getattr(Config, f'{playbook_type.name}_field_data'.lower()).vertical_one_yard
        players_data = getattr(getattr(Config, f'{playbook_type.name.lower()}_players_data'), f'{team_type.name.lower()}')
        for i, player_data in enumerate(players_data):
            team_type, position, text, symbol_type, x, y = player_data
            if playbook_type is PlaybookType.FOOTBALL:
                if team_type in (TeamType.PUNT_RET, TeamType.KICK_RET) and i == 10:
                    player_model = PlayerModel(self._playbook_model, team_type, position, text, x, y,
                                               symbol_type=symbol_type, parent=parent)
                elif team_type is TeamType.FIELD_GOAL_DEF and i == 10 and \
                        yards_to_top_border > vertical_one_yard * 11:
                    player_model = PlayerModel(self._playbook_model, team_type, position, text, x,
                                               vertical_one_yard * 4, symbol_type=symbol_type, parent=parent)
                elif team_type is TeamType.DEFENCE and i == 10 and \
                        yards_to_top_border < vertical_one_yard * 13:
                    player_model = PlayerModel(self._playbook_model, team_type, position, text, x,
                                               y + yards_to_top_border + 3 * vertical_one_yard,
                                               symbol_type=symbol_type, parent=parent)
                elif team_type is TeamType.KICK_RET and 4 < i <= 7 and \
                        yards_to_top_border == vertical_one_yard * 85:
                    player_model = PlayerModel(self._playbook_model, team_type, position, text, x,
                                               y + yards_to_top_border - vertical_one_yard * 5,
                                               symbol_type=symbol_type, parent=parent)
                elif team_type is TeamType.KICK_RET and 7 < i <= 9 and \
                        yards_to_top_border == vertical_one_yard * 85:
                    player_model = PlayerModel(self._playbook_model, team_type, position, text, x,
                                               y + yards_to_top_border - vertical_one_yard * 10,
                                               symbol_type=symbol_type, parent=parent)
                else:
                    player_model = PlayerModel(self._playbook_model, team_type, position, text, x,
                                               y + yards_to_top_border, symbol_type=symbol_type, parent=parent)
            else:
                player_model = PlayerModel(self._playbook_model, team_type, position, text, x,
                                           y + yards_to_top_border, symbol_type=symbol_type, parent=parent)
            player_models_lst.append(player_model)
        return player_models_lst

    def create_new_additional_player_model(self, parent: 'SchemeModel', first_team_position: int):
        playbook_type = self._playbook_model.playbook_type
        yards_to_top_border = self._get_yards_to_top_field_border(playbook_type, first_team_position)
        player_data = getattr(Config, f'{playbook_type.name.lower()}_players_data').additional_player
        team_type, position, text, fill_type, x, y = player_data
        return PlayerModel(self._playbook_model, team_type, position, text, x, y + yards_to_top_border,
                           fill_type=fill_type, parent=parent)

    def _get_yards_to_top_field_border(self, playbook_type: 'PlaybookType', first_team_position: int) -> int:
        field_data = getattr(Config, f'{playbook_type.name.lower()}_field_data')
        vertical_ten_yards = field_data.vertical_ten_yards
        vertical_one_yard = field_data.vertical_one_yard
        return vertical_ten_yards + vertical_one_yard * first_team_position

    def create_player_model(self, parent: 'SchemeModel', team_type: 'TeamType', position: 'PlayerPositionType',
                            text: str, x: int, y: int,
                            fill_type: Optional['FillType'] = None, symbol_type: Optional['SymbolType'] = None,
                            text_color: str = '#000000', player_color: str = '#000000',
                            uuid: Optional['UUID'] = None,
                            id_local_db: Optional[int] = None, id_api: Optional[int] = None) -> 'PlayerModel':
        return PlayerModel(self._playbook_model, team_type, position, text, x, y, fill_type, symbol_type,
                           text_color, player_color, uuid, id_local_db, id_api, parent=parent)

    def create_action_model(self, parent: 'PlayerModel', uuid: Optional['UUID'] = None,
                            id_local_db: Optional[int] = None, id_api: Optional[int] = None) -> 'ActionModel':
        return ActionModel(uuid, id_local_db, id_api, parent=parent)

    def create_action_line_model(self, parent: 'ActionModel', line_type: 'ActionLineType',
                                 x1: float, y1: float, x2: float, y2: float, thickness: int, color: str,
                                 uuid: Optional['UUID'] = None,
                                 id_local_db: Optional[int] = None, id_api: Optional[int] = None) -> 'ActionLineModel':
        return ActionLineModel(line_type, x1, y1, x2, y2, thickness, color, uuid, id_local_db, id_api, parent=parent)

    def create_final_action_model(self, parent: 'ActionModel', action_type: 'FinalActionType', x: float, y: float,
                                  angle: float, line_thickness: int, color: str, uuid: Optional['UUID'] = None,
                                  id_local_db: Optional[int] = None, id_api: Optional[int] = None) -> 'FinalActionModel':
        return FinalActionModel(action_type, x, y, angle, line_thickness, color, uuid, id_local_db, id_api, parent=parent)
