from typing import TYPE_CHECKING, Optional, Union

from sqlalchemy import text, bindparam, inspect
from sqlalchemy.orm import selectinload

from Core.logger_settings import log_method, logger
from ..mapper import PlaybookMapperLocalDB
from ..Models import PlaybookORM, SchemeORM, FigureORM, LabelORM, PencilLineORM, PlayerORM, ActionORM, \
    ActionLineORM, FinalActionORM
from .base_manager import BaseManager

if TYPE_CHECKING:
    from View_Models import PlaybookModel
    from ..DTO.output_DTO import PlaybookOutDTO, SchemeOutDTO, FigureOutDTO, LabelOutDTO, PlayerOutDTO, ActionOutDTO
    from ..DTO.input_DTO import PlaybookInputDTO

__all__ = ('PlaybookManager',)


class PlaybookManager(BaseManager):
    def __init__(self):
        super().__init__()
        self._playbook_mapper = PlaybookMapperLocalDB()

    @log_method()
    def save(self, playbook_model: 'PlaybookModel', is_new_playbook: bool = False,
             set_progress_func: Optional[callable] = None) -> 'PlaybookORM':
        if playbook_model.id_local_db and not is_new_playbook:
            return self._update(playbook_model, set_progress_func)
        else:
            with self.start_transaction():
                playbook_dto = self._playbook_mapper.get_playbook_dto(playbook_model, is_new_playbook)
                single_playbook_orm = self._playbook_mapper.create_playbook_orm(playbook_dto)
                self.session.add(single_playbook_orm)
                self.session.flush()
                playbook_id = single_playbook_orm.id
                bulk_action_lines_orm_lst: list['ActionLineORM'] = []
                bulk_final_actions_orm_lst: list['FinalActionORM'] = []
                bulk_figures_orm_lst: list['FigureORM'] = []
                bulk_labels_orm_lst: list['LabelORM'] = []
                bulk_pencil_lines_orm_lst: list['PencilLineORM'] = []
                if set_progress_func: set_progress_func(10)

                for scheme_dto in playbook_dto.schemes:
                    self._process_new_scheme_orm(
                        scheme_dto, single_playbook_orm,
                        bulk_action_lines_orm_lst, bulk_final_actions_orm_lst, bulk_figures_orm_lst,
                        bulk_labels_orm_lst, bulk_pencil_lines_orm_lst
                    )
                if set_progress_func: set_progress_func(60)

                self.session.bulk_save_objects(bulk_action_lines_orm_lst)
                self.session.bulk_save_objects(bulk_final_actions_orm_lst)
                self.session.bulk_save_objects(bulk_figures_orm_lst)
                self.session.bulk_save_objects(bulk_labels_orm_lst)
                self.session.bulk_save_objects(bulk_pencil_lines_orm_lst)
                if set_progress_func: set_progress_func(85)

                playbook_orm = self.session.get(PlaybookORM, playbook_id)
                if set_progress_func: set_progress_func(90)

                self._post_save_actions(playbook_orm)
                if set_progress_func: set_progress_func(95)
                return playbook_orm

    def _post_save_actions(self, playbook_orm: 'PlaybookORM') -> None:
        self._playbook_mapper.update_app_model_ids_from_db(playbook_orm)###################### Проверить обновление id объектов приложения

    def _process_new_scheme_orm(self, scheme_dto: 'SchemeOutDTO', parent_playbook_orm: 'PlaybookORM',
                                bulk_action_lines_orm_lst: list['ActionLineORM'],
                                bulk_final_actions_orm_lst: list['FinalActionORM'],
                                bulk_figures_orm_lst: list['FigureORM'],
                                bulk_labels_orm_lst: list['LabelORM'],
                                bulk_pencil_lines_orm_lst: list['PencilLineORM']) -> None:
        scheme_orm = self._playbook_mapper.create_scheme_orm(scheme_dto, parent_playbook_orm)
        self.session.add(scheme_orm)
        self.session.flush()
        bulk_figures_orm_lst.extend(
            [self._playbook_mapper.create_figure_orm(figure_dto, scheme_orm) for figure_dto in scheme_dto.figures]
        )
        bulk_pencil_lines_orm_lst.extend(
            [self._playbook_mapper.create_pencil_line_orm(pencil_line_dto, scheme_orm)
             for pencil_line_dto in scheme_dto.pencil_lines]
        )
        bulk_labels_orm_lst.extend(
            [self._playbook_mapper.create_label_orm(label_dto, scheme_orm) for label_dto in scheme_dto.labels]
        )
        for player_dto in scheme_dto.players:
            self._process_new_player_orm(player_dto, scheme_orm, bulk_action_lines_orm_lst, bulk_final_actions_orm_lst)

    def _process_new_player_orm(self, player_dto: 'PlayerOutDTO', parent_scheme_orm: 'SchemeORM',
                                bulk_action_lines_orm_lst: list['ActionLineORM'],
                                bulk_final_actions_orm_lst: list['FinalActionORM']) -> None:
        player_orm = self._playbook_mapper.create_player_orm(player_dto, parent_scheme_orm)
        self.session.add(player_orm)
        self.session.flush()
        for action_dto in player_dto.actions:
            self._process_new_action_orm(action_dto, player_orm, bulk_action_lines_orm_lst, bulk_final_actions_orm_lst)

    def _process_new_action_orm(self, action_dto: 'ActionOutDTO', parent_player_orm: 'PlayerORM',
                                bulk_action_lines_orm_lst: list['ActionLineORM'],
                                bulk_final_actions_orm_lst: list['FinalActionORM']) -> None:
        action_orm = self._playbook_mapper.create_action_orm(action_dto, parent_player_orm)
        self.session.add(action_orm)
        self.session.flush()
        bulk_action_lines_orm_lst.extend(
            [self._playbook_mapper.create_action_line_orm(action_line_dto, action_orm)
             for action_line_dto in action_dto.action_lines]
        )
        bulk_final_actions_orm_lst.extend(
            [self._playbook_mapper.create_final_action_orm(final_action_dto, action_orm)
             for final_action_dto in action_dto.final_actions]
        )

    @log_method()
    def _update(self, playbook_model: 'PlaybookModel', set_progress_func: Optional[callable] = None) -> 'PlaybookORM':  # Тут ещё должна быть очистка списков удалённых схем (deleted_schemes) и тд
        with self.start_transaction():
            playbook_id = playbook_model.id_local_db
            playbook_dto = self._playbook_mapper.get_playbook_dto(playbook_model, is_new_playbook=False)
            if set_progress_func: set_progress_func(10)

            bulk_action_lines_orm_lst: list['ActionLineORM'] = []
            bulk_final_actions_orm_lst: list['FinalActionORM'] = []
            bulk_figures_orm_lst: list['FigureORM'] = []
            bulk_labels_orm_lst: list['LabelORM'] = []
            bulk_pencil_lines_orm_lst: list['PencilLineORM'] = []

            self._delete_playbook_items_by_ids(
                playbook_dto.deleted_actions, playbook_dto.deleted_players, playbook_dto.deleted_figures,
                playbook_dto.deleted_labels, playbook_dto.deleted_pencil_lines, playbook_dto.deleted_schemes
            )
            if set_progress_func: set_progress_func(20)

            playbook_from_db = self.session.get(PlaybookORM, playbook_id)
            # print(f'{playbook_from_db = }')
            if set_progress_func: set_progress_func(30)

            self._update_orm_obj(playbook_dto, playbook_from_db)
            schemes_orm_dict = {scheme_orm.id: scheme_orm for scheme_orm in playbook_from_db.schemes}
            for scheme_dto in playbook_dto.schemes:
                if scheme_dto.id:
                    scheme_orm = schemes_orm_dict.get(scheme_dto.id, None)
                    if scheme_orm:
                        self._update_orm_obj(scheme_dto, scheme_orm)
                        figures_orm_dict = {figure_orm.id: figure_orm for figure_orm in scheme_orm.figures}
                        for figure_dto in scheme_dto.figures:
                            if figure_dto.id:
                                figure_orm = figures_orm_dict.get(figure_dto.id, None)
                                if figure_orm:
                                    self._update_orm_obj(figure_dto, figure_orm)
                            else:
                                new_figure_orm = self._playbook_mapper.create_figure_orm(figure_dto, scheme_orm)
                                bulk_figures_orm_lst.append(new_figure_orm)
                        labels_orm_dict = {label_orm.id: label_orm for label_orm in scheme_orm.labels}
                        for label_dto in scheme_dto.labels:
                            if label_dto.id:
                                label_orm = labels_orm_dict.get(label_dto.id, None)
                                if label_orm:
                                    self._update_orm_obj(label_dto, label_orm)
                            else:
                                new_label_orm = self._playbook_mapper.create_label_orm(label_dto, scheme_orm)
                                bulk_labels_orm_lst.append(new_label_orm)
                        for pencil_line_dto in scheme_dto.pencil_lines:
                            if pencil_line_dto.id:
                                # Линии карандаша в приложении нельзя изменить, их можно только нарисовать или удалить.
                                # Поэтому обновлять их не нужно.
                                pass
                            else:
                                new_pencil_line = self._playbook_mapper.create_pencil_line_orm(pencil_line_dto,
                                                                                               scheme_orm)
                                bulk_pencil_lines_orm_lst.append(new_pencil_line)
                        players_orm_dict = {player_orm.id: player_orm for player_orm in scheme_orm.players}
                        for player_dto in scheme_dto.players:
                            if player_dto.id:
                                player_orm = players_orm_dict.get(player_dto.id, None)
                                if player_orm:
                                    self._update_orm_obj(player_dto, player_orm)
                                    for action_dto in player_dto.actions:
                                        if action_dto.id:
                                            # Действия в приложении нельзя изменить, их можно только нарисовать или удалить.
                                            # Поэтому обновлять их не нужно
                                            pass
                                        else:
                                            self._process_new_action_orm(action_dto, player_orm,
                                                                         bulk_action_lines_orm_lst,
                                                                         bulk_final_actions_orm_lst)
                            else:
                                self._process_new_player_orm(player_dto, scheme_orm, bulk_action_lines_orm_lst,
                                                             bulk_final_actions_orm_lst)
                else:
                    self._process_new_scheme_orm(
                        scheme_dto, playbook_from_db, bulk_action_lines_orm_lst,
                        bulk_final_actions_orm_lst, bulk_figures_orm_lst, bulk_labels_orm_lst,
                        bulk_pencil_lines_orm_lst
                    )
            self.session.flush()
            if set_progress_func: set_progress_func(60)

            self.session.bulk_save_objects(bulk_action_lines_orm_lst)
            self.session.bulk_save_objects(bulk_final_actions_orm_lst)
            self.session.bulk_save_objects(bulk_figures_orm_lst)
            self.session.bulk_save_objects(bulk_labels_orm_lst)
            self.session.bulk_save_objects(bulk_pencil_lines_orm_lst)
            if set_progress_func: set_progress_func(70)

            for scheme_orm in playbook_from_db.schemes:
                for player_orm in scheme_orm.players:
                    for action_orm in player_orm.actions:
                        self.session.expire(action_orm)
                self.session.expire(scheme_orm)
            if set_progress_func: set_progress_func(85)

            # print(f'{playbook_from_db = }')
            self._post_save_actions(playbook_from_db)
            if set_progress_func: set_progress_func(95)
            return playbook_from_db

    @log_method()
    def _delete_playbook_items_by_ids(self, deleted_actions: list[int], deleted_players: list[int],
                                      deleted_figures: list[int], deleted_labels: list[int],
                                      deleted_pencil_lines: list[int], deleted_schemes: list[int]) -> None:
        if deleted_actions:
            delete_action_lines_query = text('DELETE FROM actions WHERE id IN :ids').bindparams(bindparam('ids', expanding=True))
            self.session.execute(delete_action_lines_query, {'ids': tuple(deleted_actions)})
        if deleted_players:
            delete_players_query = text('DELETE FROM players WHERE id IN :ids').bindparams(
                bindparam('ids', expanding=True))
            self.session.execute(delete_players_query, {'ids': tuple(deleted_players)})
        if deleted_figures:
            delete_figures_query = text('DELETE FROM figures WHERE id IN :ids').bindparams(
                bindparam('ids', expanding=True))
            self.session.execute(delete_figures_query, {'ids': tuple(deleted_figures)})
        if deleted_labels:
            delete_labels_query = text('DELETE FROM labels WHERE id IN :ids').bindparams(
                bindparam('ids', expanding=True))
            self.session.execute(delete_labels_query, {'ids': tuple(deleted_labels)})
        if deleted_pencil_lines:
            delete_pencil_lines_query = text('DELETE FROM pencil_lines WHERE id IN :ids').bindparams(
                bindparam('ids', expanding=True))
            self.session.execute(delete_pencil_lines_query, {'ids': tuple(deleted_pencil_lines)})
        if deleted_schemes:
            delete_schemes_query = text('DELETE FROM schemes WHERE id IN :ids').bindparams(
                bindparam('ids', expanding=True))
            self.session.execute(delete_schemes_query, {'ids': tuple(deleted_schemes)})

    @log_method()
    def _update_orm_obj(self, dto_obj: Union['PlaybookOutDTO', 'SchemeOutDTO', 'FigureOutDTO', 'LabelOutDTO', 'PlayerOutDTO'],
                        orm_obj: Union['PlaybookORM', 'SchemeORM', 'FigureORM', 'LabelORM', 'PlayerORM']) -> None:
        dto_data = dto_obj.model_dump()
        orm_mapper = inspect(orm_obj).mapper
        for column in orm_mapper.columns:
            attr_name = column.key
            if attr_name in dto_data:
                orm_value = getattr(orm_obj, attr_name)
                dto_value = dto_data[attr_name]
                if orm_value != dto_value:
                    setattr(orm_obj, attr_name, dto_value)

    def _get_by_id(self, playbook_id: int) -> Optional['PlaybookORM']:
        with self.start_transaction():
            return self.session.get(PlaybookORM, playbook_id)
            # playbook_orm = self.session.query(PlaybookORM)\
            #     .options(selectinload(PlaybookORM.schemes)
            #              .options(selectinload(SchemeORM.figures), selectinload(SchemeORM.labels),
            #                       selectinload(SchemeORM.pencil_lines), selectinload(SchemeORM.players)
            #                       .options(selectinload(PlayerORM.actions)
            #                                .options(selectinload(ActionORM.action_lines),
            #                                         selectinload(ActionORM.final_actions)
            #                                         )
            #                                )
            #                       )
            #              ).get(playbook_id)
            # return playbook_orm

    @log_method()
    def get_playbook_dto_by_id(self, playbook_id: int) -> Optional['PlaybookInputDTO']:
        playbook_orm = self._get_by_id(playbook_id)
        if playbook_orm:
            return self._playbook_mapper.orm_to_dto(playbook_orm)
        return None

    @log_method()
    def delete_by_id(self, obj_id: int) -> None:
        with self.start_transaction():
            query = text('DELETE FROM playbooks WHERE id = :id').bindparams(id=obj_id)
            self.session.execute(query)

    @log_method()
    def get_all_obj_info(self) -> list[tuple]:
        with self.start_transaction():
            query = text('SELECT id, name, playbook_type, updated_at, created_at FROM playbooks')
            res = self.session.execute(query)
            return res.all()


