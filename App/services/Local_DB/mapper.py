from typing import TYPE_CHECKING, Union, Any, Generic

from abc import abstractmethod

from Core.logger_settings import log_method, logger
from Core.Enums import StorageType
from View_Models import PlaybookModel
from .DTO import PlaybookOutDTO, PlaybookInputDTO
from Services.Common.validators_DTO import validate_playbook_type
from .Models import PlaybookORM, SchemeORM, FigureORM, LabelORM, PencilLineORM, PlayerORM, ActionORM, \
    ActionLineORM, FinalActionORM
from Services.Common.base_mapper import T, M, O

if TYPE_CHECKING:
    from uuid import UUID
    from View_Models import SchemeModel, FigureModel, LabelModel, PencilLineModel, PlayerModel, ActionModel, ActionLineModel, FinalActionModel
    from .DTO.output_DTO import SchemeOutDTO, PlayerOutDTO, ActionOutDTO, FigureOutDTO, LabelOutDTO, PencilLineOutDTO, ActionLineOutDTO, FinalActionOutDTO


class ORMMapperMixin(Generic[O]):
    @abstractmethod
    def _dto_to_orm(self, item: T) -> O:
        pass

    @abstractmethod
    def _orm_to_dto(self, item: O) -> M:
        pass


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
                                                'PencilLineModel', 'PlayerModel', 'ActionModel',
                                                'ActionLineModel', 'FinalActionModel']) -> dict:
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
                                              'PencilLineModel', 'PlayerModel', 'ActionModel',
                                              'ActionLineModel', 'FinalActionModel']) -> None:
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
            'actions': [self._process_action(is_new_playbook, action_model) for action_model in player_model.actions],
        })
        return player_dict

    def _process_action(self, is_new_playbook: bool,  action_model: 'ActionModel') -> dict[str, Any]:
        action_dict = self._get_model_dict_for_saving(is_new_playbook, action_model)
        action_dict.update({
            'action_lines': [self._get_model_dict_for_saving(is_new_playbook, action_line_model)
                             for action_line_model in action_model.action_lines],
            'final_actions': [self._get_model_dict_for_saving(is_new_playbook, final_action_model)
                              for final_action_model in action_model.final_actions]
        })
        return action_dict

    def _playbook_model_to_dict(self, is_new_playbook: bool,  playbook_model: 'PlaybookModel') -> dict[str, Any]:
        return self._get_playbook_dict(is_new_playbook, playbook_model)

    def _playbook_model_to_dto(self, is_new_playbook: bool,  playbook_model: 'PlaybookModel') -> 'PlaybookOutDTO':
        playbook_dict = self._get_playbook_dict(is_new_playbook, playbook_model)
        playbook_type = playbook_dict.get('playbook_type')
        validate_playbook_type(playbook_type)
        return PlaybookOutDTO.model_validate(playbook_dict, context={"playbook_type": playbook_type})

    @log_method()
    def get_playbook_dto(self, playbook_model: 'PlaybookModel', is_new_playbook: bool) -> 'PlaybookOutDTO':
        '''Получение провалидированного DTO-объекта для дальнейшего преобразования его в ORM-объект локальной БД
         или для сериализации и отправки на API'''
        return self._playbook_model_to_dto(is_new_playbook, playbook_model)

    def _create_playbook_orm_with_nested_items(self, is_new_playbook: bool, playbook: 'PlaybookModel') -> 'PlaybookORM':  # НЕ ИСПОЛЬЗУЕТСЯ
        playbook_dto = self.get_playbook_dto(playbook, is_new_playbook)
        playbook_orm = PlaybookORM(**playbook_dto.model_dump(exclude={'schemes'}))
        for scheme_dto in playbook_dto.schemes:
            playbook_orm.schemes.append(self.create_scheme_orm_with_nested_items(scheme_dto))
        return playbook_orm

    @log_method()
    def create_scheme_orm_with_nested_items(self, scheme_dto: 'SchemeOutDTO') -> 'SchemeORM':  # НЕ ИСПОЛЬЗУЕТСЯ
        scheme_orm = SchemeORM(**scheme_dto.model_dump(exclude={'figures', 'labels', 'pencil_lines', 'players'}))
        scheme_orm.figures.extend(FigureORM(**figure.model_dump()) for figure in scheme_dto.figures)
        scheme_orm.labels.extend(LabelORM(**label.model_dump()) for label in scheme_dto.labels)
        scheme_orm.pencil_lines.extend(PencilLineORM(**pencil_line.model_dump()) for pencil_line in scheme_dto.pencil_lines)
        for player_dto in scheme_dto.players:
            scheme_orm.players.append(self.create_player_orm_with_nested_items(player_dto))
        return scheme_orm

    @log_method()
    def create_player_orm_with_nested_items(self, player_dto: 'PlayerOutDTO') -> 'PlayerORM':  # НЕ ИСПОЛЬЗУЕТСЯ
        player_orm = PlayerORM(**player_dto.model_dump(exclude={'actions'}))
        for action_dto in player_dto.actions:
            player_orm.actions.append(self.create_action_orm_with_nested_items(action_dto))
        return player_orm

    @log_method()
    def create_action_orm_with_nested_items(self, action_dto: 'ActionOutDTO') -> 'ActionORM':  # НЕ ИСПОЛЬЗУЕТСЯ
        action_orm = ActionORM(**action_dto.model_dump(exclude={'action_lines', 'final_actions'}))
        action_orm.action_lines.extend(ActionLineORM(**line.model_dump()) for line in action_dto.action_lines)
        action_orm.final_actions.extend(FinalActionORM(**final_action.model_dump()) for final_action in action_dto.final_actions)
        return action_orm

    @log_method()
    def get_playbook_orm(self, playbook_model: 'PlaybookModel', is_new_playbook: bool) -> 'PlaybookORM':  # НЕ ИСПОЛЬЗУЕТСЯ
        '''Получение готового к сохранению в локальной БД ORM-объекта плейбука со всеми вложенными объектами схем и тд.'''
        return self._create_playbook_orm_with_nested_items(is_new_playbook, playbook_model)

    @log_method()
    def create_playbook_orm(self, playbook_dto: 'PlaybookOutDTO') -> 'PlaybookORM':
        return PlaybookORM(**playbook_dto.model_dump(exclude={'schemes'}))

    @log_method()
    def create_scheme_orm(self, scheme_dto: 'SchemeOutDTO', playbook_orm: 'PlaybookORM') -> 'SchemeORM':
        return SchemeORM(**scheme_dto.model_dump(exclude={'figures', 'labels', 'pencil_lines', 'players'}),
                         playbook=playbook_orm, playbook_id=playbook_orm)

    @log_method()
    def create_player_orm(self, player_dto: 'PlayerOutDTO', scheme_orm: 'SchemeORM') -> 'PlayerORM':
        return PlayerORM(**player_dto.model_dump(exclude={'actions'}), scheme=scheme_orm, scheme_id=scheme_orm.id)

    @log_method()
    def create_action_orm(self, action_dto: 'ActionOutDTO', player_orm: 'PlayerORM') -> 'ActionORM':
        return ActionORM(**action_dto.model_dump(exclude={'action_lines', 'final_actions'}),
                         player=player_orm, player_id=player_orm.id)

    @log_method()
    def create_action_line_orm(self, action_line_dto: 'ActionLineOutDTO', action_orm: 'ActionORM') -> 'ActionLineORM':
        action_line_orm = ActionLineORM(**action_line_dto.model_dump())
        action_line_orm.action_id = action_orm.id
        return action_line_orm

    @log_method()
    def create_final_action_orm(self, final_action_dto: 'FinalActionOutDTO', action_orm: 'ActionORM') -> 'FinalActionORM':
        final_action_orm = FinalActionORM(**final_action_dto.model_dump())
        final_action_orm.action_id = action_orm.id
        return final_action_orm

    @log_method()
    def create_figure_orm(self, figure_dto: 'FigureOutDTO', scheme_orm: 'SchemeORM') -> 'FigureORM':
        figure_orm = FigureORM(**figure_dto.model_dump())
        figure_orm.scheme_id = scheme_orm.id
        return figure_orm

    @log_method()
    def create_label_orm(self, label_dto: 'LabelOutDTO', scheme_orm: 'SchemeORM') -> 'LabelORM':
        label_orm = LabelORM(**label_dto.model_dump())
        label_orm.scheme_id = scheme_orm.id
        return label_orm

    @log_method()
    def create_pencil_line_orm(self, pencil_line_dto: 'PencilLineOutDTO', scheme_orm: 'SchemeORM') -> 'PencilLineORM':
        pencil_line_orm = PencilLineORM(**pencil_line_dto.model_dump())
        pencil_line_orm.scheme_id = scheme_orm.id
        return pencil_line_orm

    @log_method()
    def update_app_model_ids_from_db(self, playbook_orm: 'PlaybookORM') -> dict:
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
                    # for action_part_orm in chain(action_orm.action_lines, action_orm.final_actions):
                    #     self._update_model_id(action_part_orm)
        return self._id_mapping

    def _update_model_id(self, orm_obj: Union['SchemeORM', 'FigureORM', 'LabelORM', 'PencilLineORM',
                                              'PlayerORM', 'ActionORM', 'ActionLineORM', 'FinalActionORM']) -> None:
        model = self._id_mapping.pop(orm_obj.uuid)
        model.id_local_db = orm_obj.id

    def _update_playbook_model(self, orm_obj: 'PlaybookORM') -> None:
        playbook_model = self._id_mapping.pop(orm_obj.uuid)
        playbook_model.id_local_db = orm_obj.id
        playbook_model.clear_deleted_item_ids(StorageType.LOCAL_DB)

    @log_method()
    def orm_to_dto(self, playbook_orm: 'PlaybookORM') -> 'PlaybookInputDTO':
        playbook_dto = PlaybookInputDTO.model_validate(playbook_orm)
        return playbook_dto

