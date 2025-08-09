from typing import TYPE_CHECKING, Optional, Union, Any, Generic
from dataclasses import dataclass, field

from abc import abstractmethod

from Config.Enums import StorageType
from Models import PlaybookModel
from .DTO.output_DTO import PlaybookOutDTO, SchemeOutDTO, PlayerOutDTO, ActionOutDTO
from services.common.validators import validate_playbook_type
from services.Local_DB.models import PlaybookORM, SchemeORM, FigureORM, LabelORM, PencilLineORM, PlayerORM, ActionORM, \
    ActionLineORM, FinalActionORM
from services.common.base_mapper import BaseMapper, T, M, O

if TYPE_CHECKING:
    from uuid import UUID
    from Models import SchemeModel, FigureModel, LabelModel, PencilLineModel, PlayerModel, ActionModel


class ORMMapperMixin(Generic[O]):
    @abstractmethod
    def _dto_to_orm(self, item: T) -> O:
        pass

    @abstractmethod
    def _orm_to_dto(self, item: O) -> M:
        pass


@dataclass
class IDMapping:
    playbook: dict[int, 'PlaybookModel'] = field(default_factory=dict)
    schemes: dict[int, 'SchemeModel'] = field(default_factory=dict)
    figures: dict[int, 'FigureModel'] = field(default_factory=dict)
    labels: dict[int, 'LabelModel'] = field(default_factory=dict)
    pencil_lines: dict[int, 'PencilLineModel'] = field(default_factory=dict)
    players: dict[int, 'PlayerModel'] = field(default_factory=dict)
    action: dict[int, 'ActionModel'] = field(default_factory=dict)


# class PlaybookMapperLocalDB(BaseMapper[PlaybookWidget, PlaybookOutDTO], ORMMapperMixin[PlaybookORM]):
class PlaybookMapperLocalDB():
    def __init__(self):
        self._id_mapping: dict['UUID': Union['PlaybookModel', 'SchemeModel', 'FigureModel', 'LabelModel',
                                             'PencilLineModel', 'PlayerModel', 'ActionModel']] = {}

    def _get_playbook_dict(self, is_new_playbook: bool, playbook_model: 'PlaybookModel') -> dict:
        playbook_dict = self._get_model_dict_for_saving(is_new_playbook, playbook_model)
        playbook_dict['schemes'] = [self._process_scheme(is_new_playbook, scheme_model, i) for i, scheme_model in enumerate(playbook_model.schemes)]
        return playbook_dict

    def _get_model_dict_for_saving(self, is_new_playbook: bool,
                                   model: Union['PlaybookModel', 'SchemeModel', 'FigureModel', 'LabelModel',
                                                'PencilLineModel', 'PlayerModel', 'ActionModel']) -> dict:
        model_dict = model.to_dict()
        model_dict['id'] = None if is_new_playbook else model.id_local_db
        if isinstance(model, PlaybookModel):
            model_dict['deleted_schemes'] = model.get_deleted_item_ids('schemes', StorageType.LOCAL_DB)
            model_dict['deleted_figures'] = model.get_deleted_item_ids('figures', StorageType.LOCAL_DB)
            model_dict['deleted_labels'] = model.get_deleted_item_ids('labels', StorageType.LOCAL_DB)
            model_dict['deleted_pencil_lines'] = model.get_deleted_item_ids('pencil_lines', StorageType.LOCAL_DB)
            model_dict['deleted_players'] = model.get_deleted_item_ids('players', StorageType.LOCAL_DB)
            model_dict['deleted_actions'] = model.get_deleted_item_ids('actions', StorageType.LOCAL_DB)
        self._add_to_id_mapping(model)
        return model_dict

    def _add_to_id_mapping(self, model: Union['PlaybookModel', 'SchemeModel', 'FigureModel', 'LabelModel',
                                              'PencilLineModel', 'PlayerModel', 'ActionModel']) -> None:
        self._id_mapping[model.uuid] = model

    def _process_scheme(self, is_new_playbook: bool, scheme_model: 'SchemeModel', index: int) -> dict[str, Any]:
        scheme_dict = self._get_model_dict_for_saving(is_new_playbook, scheme_model)
        scheme_dict.update({'row_index': index})
        scheme_dict.update({
            'figures': [self._get_model_dict_for_saving(is_new_playbook, figure_model) for figure_model in scheme_model.figures],
            'labels': [self._get_model_dict_for_saving(is_new_playbook, label_model) for label_model in scheme_model.labels],
            'pencil_lines': [self._get_model_dict_for_saving(is_new_playbook, pencil_line_model) for pencil_line_model in scheme_model.pencil_lines],
            'players': self._process_players(is_new_playbook, scheme_model)
        })
        return scheme_dict

    def _process_players(self, is_new_playbook: bool, scheme_model: 'SchemeModel') -> list[dict[str, Any]]:
        player_dicts_lst = []
        for player_model in scheme_model.first_team_players:
            player_dicts_lst.append(self._process_single_player(is_new_playbook, player_model))
        for player_model in scheme_model.second_team_players:
            player_dicts_lst.append(self._process_single_player(is_new_playbook, player_model))
        if scheme_model.additional_player:
            player_dicts_lst.append(self._process_single_player(is_new_playbook, scheme_model.additional_player))
        return player_dicts_lst

    def _process_single_player(self, is_new_playbook: bool,  player_model: 'PlayerModel') -> dict[str, Any]:
        player_dict = self._get_model_dict_for_saving(is_new_playbook, player_model)
        player_dict.update({
            'actions': [self._get_model_dict_for_saving(is_new_playbook, action_model) for action_model in player_model.actions],
        })
        return player_dict

    def _playbook__model_to_dict(self, is_new_playbook: bool,  playbook_model: 'PlaybookModel') -> dict[str, Any]:
        return self._get_playbook_dict(is_new_playbook, playbook_model)

    def _playbook_model_to_dto(self, is_new_playbook: bool,  playbook_model: 'PlaybookModel') -> 'PlaybookOutDTO':
        playbook_dict = self._get_playbook_dict(is_new_playbook, playbook_model)
        playbook_type = playbook_dict.get('playbook_type')
        validate_playbook_type(playbook_type)
        return PlaybookOutDTO.model_validate(playbook_dict, context={"playbook_type": playbook_type})

    def get_playbook_dto(self, playbook_model: 'PlaybookModel', is_new_playbook: bool) -> 'PlaybookOutDTO':
        '''Получение провалидированного DTO-объекта для дальнейшего преобразования его в ORM-объект локальной БД
         или для сериализации и отправки на API'''
        return self._playbook_model_to_dto(is_new_playbook, playbook_model)

    def _playbook_model_to_orm(self, is_new_playbook: bool, playbook: 'PlaybookModel') -> 'PlaybookORM':
        playbook_dto = self.get_playbook_dto(playbook, is_new_playbook)
        playbook_orm = PlaybookORM(id=playbook_dto.id, uuid=playbook_dto.uuid, name=playbook_dto.name,
                                   playbook_type=playbook_dto.playbook_type, info=playbook_dto.info,
                                   schemes=list(),
                                   deleted_schemes=playbook_dto.deleted_schemes,
                                   deleted_figures=playbook_dto.deleted_figures,
                                   deleted_labels=playbook_dto.deleted_labels,
                                   deleted_pencil_lines=playbook_dto.deleted_pencil_lines,
                                   deleted_players=playbook_dto.deleted_players,
                                   deleted_actions=playbook_dto.deleted_actions)
        for scheme_dto in playbook_dto.schemes:
            playbook_orm.schemes.append(self.create_scheme_orm(scheme_dto))
        return playbook_orm

    def create_scheme_orm(self, scheme_dto: 'SchemeOutDTO') -> 'SchemeORM':
        scheme_orm = SchemeORM(id=scheme_dto.id, uuid=scheme_dto.uuid, name=scheme_dto.name,
                               row_index=scheme_dto.row_index, zoom=scheme_dto.zoom,
                               view_point_x=scheme_dto.view_point_x, view_point_y=scheme_dto.view_point_y,
                               first_team=scheme_dto.first_team, second_team=scheme_dto.second_team,
                               first_team_position=scheme_dto.first_team_position, note=scheme_dto.note,
                               figures=list(), labels=list(), pencil_lines=list(), players=list())
        scheme_orm.figures.extend(FigureORM(**figure.model_dump()) for figure in scheme_dto.figures)
        scheme_orm.labels.extend(LabelORM(**label.model_dump()) for label in scheme_dto.labels)
        scheme_orm.pencil_lines.extend(PencilLineORM(**pencil_line.model_dump()) for pencil_line in scheme_dto.pencil_lines)
        for player_dto in scheme_dto.players:
            scheme_orm.players.append(self.create_player_orm(player_dto))
        return scheme_orm

    def create_player_orm(self, player_dto: 'PlayerOutDTO') -> 'PlayerORM':
        player_orm = PlayerORM(id=player_dto.id, uuid=player_dto.uuid, x=player_dto.x, y=player_dto.y,
                               team_type=player_dto.team_type, position=player_dto.position,
                               text=player_dto.text, text_color=player_dto.text_color, player_color=player_dto.player_color,
                               fill_type=player_dto.fill_type, symbol_type=player_dto.symbol_type,
                               actions=list())
        for action_dto in player_dto.actions:
            player_orm.actions.append(self.create_action_orm(action_dto))
        return player_orm

    def create_action_orm(self, action_dto: 'ActionOutDTO') -> 'ActionORM':
        action_orm = ActionORM(id=action_dto.id, uuid=action_dto.uuid,
                               lines=list(), final_actions=list())
        action_orm.lines.extend(ActionLineORM(**line.model_dump()) for line in action_dto.lines)
        action_orm.final_actions.extend(FinalActionORM(**final_action.model_dump()) for final_action in action_dto.final_actions)
        return action_orm

    def get_playbook_orm(self, playbook_model: 'PlaybookModel', is_new_playbook: bool) -> 'PlaybookORM':
        '''Получение готового к сохранению в локальной БД ORM-объекта плейбука'''
        return self._playbook_model_to_orm(is_new_playbook, playbook_model)

    def update_app_model_ids_from_db(self, playbook_orm: 'PlaybookORM') -> None:
        '''Обновление id_local_db (id из локальной БД) для объектов приложения.
         ДОЛЖЕН ВЫЗЫВАТЬСЯ ПОСЛЕ СОХРАНЕНИЯ ПЛЕЙБУКА В ЛОКАЛЬНУЮ БД'''
        self._update_playbook_model(playbook_orm)
        for scheme_orm in playbook_orm.schemes:
            self._update_model_id(scheme_orm)
            for figure_orm in scheme_orm.figures:
                self._update_model_id(figure_orm)
            for label_orm in scheme_orm.labels:
                self._update_model_id(label_orm)
            for pencil_line_orm in scheme_orm.pencil_lines:
                self._update_model_id(pencil_line_orm)
            for player_orm in scheme_orm.players:
                self._update_model_id(player_orm)
                for action_orm in player_orm.actions:
                    self._update_model_id(action_orm)
        print(f'{self._id_mapping = }')
        # self._id_mapping.clear()

    def _update_model_id(self, orm_obj: Union['SchemeORM', 'FigureORM', 'LabelORM', 'PencilLineORM',
                                              'PlayerORM', 'ActionORM']) -> None:
        model = self._id_mapping.pop(orm_obj.uuid)
        model.id_local_db = orm_obj.id

    def _update_playbook_model(self, orm_obj: 'PlaybookORM') -> None:
        playbook_model = self._id_mapping.pop(orm_obj.uuid)
        playbook_model.id_local_db = orm_obj.id
        playbook_model.clear_deleted_item_ids(StorageType.LOCAL_DB)



    def _orm_to_dto(self, playbook: 'PlaybookORM') -> 'PlaybookOutDTO':
        pass

    def _dto_to_app_obj(self, playbook: 'PlaybookOutDTO') -> 'PlaybookWidget':
        pass

