from typing import TYPE_CHECKING, Optional

from sqlalchemy import text, bindparam
from services.Local_DB.mappers import PlaybookMapperLocalDB
from services.Local_DB.models import PlaybookORM, SchemeORM, FigureORM, LabelORM, PencilLineORM, PlayerORM, ActionLineORM, FinalActionORM


if TYPE_CHECKING:
    from sqlalchemy.orm import Session
    from Models import PlaybookModel
    from ..DTO.output_DTO import SchemeOutDTO, FigureOutDTO, LabelOutDTO, PlayerOutDTO

__all__ = ('PlaybookManager',)


class PlaybookManager:
    def __init__(self, db: 'Session'):  # транзакции
        self.db = db
        self._playbook_mapper = PlaybookMapperLocalDB()

    def save(self, playbook_model: 'PlaybookModel', is_new_playbook: bool = False,
             set_progress_func: Optional[callable] = None) -> 'PlaybookORM':  # Много запросов, сделать bulk
        if playbook_model.id_local_db and not is_new_playbook:
            return self._update(playbook_model, set_progress_func)
        else:
            try:
                with self.db.begin():
                    playbook_orm = self._flush_playbook(playbook_model, is_new_playbook)
                    if set_progress_func: set_progress_func(80)
                    self._post_commit_actions(playbook_orm)
                    if set_progress_func: set_progress_func(95)
                    return playbook_orm
            except Exception as e:
                self.db.rollback()
                raise e

    def _flush_playbook(self, playbook_model: 'PlaybookModel', is_new_playbook: bool) -> 'PlaybookORM':
        playbook_orm = self._playbook_mapper.get_playbook_orm(playbook_model, is_new_playbook=is_new_playbook)
        self.db.add(playbook_orm)
        self.db.flush()
        return playbook_orm

    def _post_commit_actions(self, playbook_orm: 'PlaybookORM') -> None:
        self._playbook_mapper.update_app_model_ids_from_db(playbook_orm)###################### Проверить обновление id объектов приложения

    def _update(self, playbook_model: 'PlaybookModel', set_progress_func: Optional[callable] = None) -> 'PlaybookORM':  # Тут ещё должна быть очистка списков удалённых схем (deleted_schemes) и тд
        playbook_id = playbook_model.id_local_db
        mapper = PlaybookMapperLocalDB()
        playbook_dto = mapper.get_playbook_dto(playbook_model, is_new_playbook=False)
        # print(f'{playbook_dto = }')
        if set_progress_func: set_progress_func(10)
        if playbook_dto.deleted_actions:
            delete_action_lines_query = text('DELETE FROM actions WHERE id IN :ids').bindparams(bindparam('ids', expanding=True))
            self.db.execute(delete_action_lines_query, {'ids': tuple(playbook_dto.deleted_actions)})
        if playbook_dto.deleted_players:
            delete_players_query = text('DELETE FROM players WHERE id IN :ids').bindparams(bindparam('ids', expanding=True))
            self.db.execute(delete_players_query, {'ids': tuple(playbook_dto.deleted_players)})
        if playbook_dto.deleted_figures:
            delete_figures_query = text('DELETE FROM figures WHERE id IN :ids').bindparams(bindparam('ids', expanding=True))
            self.db.execute(delete_figures_query, {'ids': tuple(playbook_dto.deleted_figures)})
        if playbook_dto.deleted_labels:
            delete_labels_query = text('DELETE FROM labels WHERE id IN :ids').bindparams(bindparam('ids', expanding=True))
            self.db.execute(delete_labels_query, {'ids': tuple(playbook_dto.deleted_labels)})
        if playbook_dto.deleted_pencil_lines:
            delete_pencil_lines_query = text('DELETE FROM pencil_lines WHERE id IN :ids').bindparams(bindparam('ids', expanding=True))
            self.db.execute(delete_pencil_lines_query, {'ids': tuple(playbook_dto.deleted_pencil_lines)})
        if playbook_dto.deleted_schemes:
            delete_schemes_query = text('DELETE FROM schemes WHERE id IN :ids').bindparams(bindparam('ids', expanding=True))
            self.db.execute(delete_schemes_query, {'ids': tuple(playbook_dto.deleted_schemes)})
        if set_progress_func: set_progress_func(20)
        playbook_from_db = self.db.get(PlaybookORM, playbook_id)
        # print(f'{playbook_from_db = }')
        if set_progress_func: set_progress_func(30)

        playbook_from_db.name, playbook_from_db.playbook_type, playbook_from_db.info = \
            playbook_dto.name, playbook_dto.playbook_type, playbook_dto.info
        for scheme_dto in playbook_dto.schemes:
            if scheme_dto.id:
                scheme_orm = playbook_from_db.schemes[playbook_from_db.schemes.index(scheme_dto)]
                # У модели ORM-схемы переопределён метод __eq__. Он сравнивает id DTO-модели и id ORM-модели.
                # Это позволяет находить index ORM-модели соответствующей DTO-модели.
                self._update_scheme_orm(scheme_dto, scheme_orm)
            else:
                new_scheme_orm = mapper.create_scheme_orm_with_nested_items(
                    scheme_dto)  # создаётся схема и все вложенные объекты (фигуры, надписи и тд.)
                playbook_from_db.schemes.append(new_scheme_orm)
                continue
            for figure_dto in scheme_dto.figures:
                if figure_dto.id:
                    figure_orm = scheme_orm.figures[scheme_orm.figures.index(figure_dto)]
                    # У модели ORM-фигуры переопределён метод __eq__. Он сравнивает id DTO-модели и id ORM-модели.
                    # Это позволяет находить index ORM-модели соответствующей DTO-модели.
                    self._update_figure_orm(figure_dto, figure_orm)
                else:
                    new_figure_orm = FigureORM(**figure_dto.model_dump())
                    scheme_orm.figures.append(new_figure_orm)
            for label_dto in scheme_dto.labels:
                if label_dto.id:
                    label_orm = scheme_orm.labels[scheme_orm.labels.index(label_dto)]
                    # У модели ORM-надписи переопределён метод __eq__. Он сравнивает id DTO-модели и id ORM-модели.
                    # Это позволяет находить index ORM-модели соответствующей DTO-модели.
                    self._update_label_orm(label_dto, label_orm)
                else:
                    new_label_orm = LabelORM(**label_dto.model_dump())
                    scheme_orm.labels.append(new_label_orm)
            for pencil_line_dto in scheme_dto.pencil_lines:
                if pencil_line_dto.id:
                    pass
                    # Линии карандаша в приложении нельзя изменить.
                    # Их можно только нарисовать или удалить, поэтому обновлять их не нужно.
                else:
                    new_pencil_line = PencilLineORM(**pencil_line_dto.model_dump())
                    scheme_orm.pencil_lines.append(new_pencil_line)
            for player_dto in scheme_dto.players:
                if player_dto.id:
                    player_orm = scheme_orm.players[scheme_orm.players.index(player_dto)]
                    # У модели ORM-игрока переопределён метод __eq__. Он сравнивает id DTO-модели и id ORM-модели.
                    # Это позволяет находить index ORM-модели соответствующей DTO-модели.
                    self._update_player_orm(player_dto, player_orm)
                else:
                    new_player_orm = mapper.create_player_orm_with_nested_items(
                        player_dto)  # создаётся игрок и все вложенные объекты (действия)
                    scheme_orm.players.append(new_player_orm)
                    continue
                for action_dto in player_dto.actions:
                    if action_dto.id:
                        pass
                        # Действия в приложении нельзя изменить.
                        # Их можно только нарисовать или удалить, поэтому обновлять их не нужно
                    else:
                        new_action_orm = mapper.create_action_orm(action_dto)  # создаётся действие и все вложенные объекты(линии и финальные действия)
                        player_orm.actions.append(new_action_orm)
        self.db.add(playbook_from_db)

        self.db.commit()
        if set_progress_func: set_progress_func(80)
        mapper.update_app_model_ids_from_db(playbook_from_db)
        # print(f'{playbook_from_db = }')
        if set_progress_func: set_progress_func(95)


        return playbook_from_db




    def _update_scheme_orm(self, scheme_dto: 'SchemeOutDTO', scheme_orm: 'SchemeORM') -> None:
        scheme_orm.name, scheme_orm.row_index, scheme_orm.zoom, scheme_orm.view_point_x, scheme_orm.view_point_y, scheme_orm.first_team, scheme_orm.second_team, scheme_orm.first_team_position, scheme_orm.note = \
        scheme_dto.name, scheme_dto.row_index, scheme_dto.zoom, scheme_dto.view_point_x, scheme_dto.view_point_y, scheme_dto.first_team, scheme_dto.second_team, scheme_dto.first_team_position, scheme_dto.note

    def _update_figure_orm(self, figure_dto: 'FigureOutDTO', figure_orm: 'FigureORM') -> None:
        figure_orm.x, figure_orm.y, figure_orm.width, figure_orm.height, figure_orm.figure_type, figure_orm.border, figure_orm.border_thickness, figure_orm.border_color, figure_orm.fill, figure_orm.fill_opacity, figure_orm.fill_color = \
        figure_dto.x, figure_dto.y, figure_dto.width, figure_dto.height, figure_dto.figure_type, figure_dto.border, figure_dto.border_thickness, figure_dto.border_color, figure_dto.fill, figure_dto.fill_opacity, figure_dto.fill_color

    def _update_label_orm(self, label_dto: 'LabelOutDTO', label_orm: 'LabelORM') -> None:
        label_orm.x, label_orm.y, label_orm.width, label_orm.height, label_orm.text, label_orm.font_type, label_orm.font_size, label_orm.font_bold, label_orm.font_italic, label_orm.font_underline, label_orm.font_color = \
        label_dto.x, label_dto.y, label_dto.width, label_dto.height, label_dto.text, label_dto.font_type, label_dto.font_size, label_dto.font_bold, label_dto.font_italic, label_dto.font_underline, label_dto.font_color

    def _update_player_orm(self, player_dto: 'PlayerOutDTO', player_orm: 'PlayerORM') -> None:
        player_orm.x, player_orm.y, player_orm.team_type, player_orm.position, player_orm.text, player_orm.text_color, player_orm.player_color, player_orm.fill_type, player_orm.symbol_type = \
        player_dto.x, player_dto.y, player_dto.team_type, player_dto.position, player_dto.text, player_dto.text_color, player_dto.player_color, player_dto.fill_type, player_dto.symbol_type

    def get_by_id(self, obj_id: int) -> Optional['PlaybookORM']:
        return self.db.get(PlaybookORM, obj_id)

    def delete_by_id(self, obj_id: int) -> None:  # Проверить каскадное удаление
        # deleted_playbook = self.get_by_id(obj_id)
        # self.db.delete(deleted_playbook)
        # self.db.commit()
        query = text('DELETE FROM playbooks WHERE id = :id')
        query = query.bindparams(id=obj_id)
        self.db.execute(query)
        self.db.commit()

    def get_all_obj_info(self):
        query = text('SELECT id, name, playbook_type, updated_at, created_at FROM playbooks')
        res = self.db.execute(query)
        return res.all()


