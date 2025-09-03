from typing import TYPE_CHECKING, Optional, NamedTuple

from PySide6.QtCore import QRect, Qt, QBuffer, QByteArray
from PySide6.QtGui import QUndoStack, QImage, QPainter
from PySide6.QtWidgets import QFileDialog

import Config
from Core import log_method, logger
from Core.settings import UNDO_STACK_LIMIT
from Commands import (PlaceFirstTeamCommand, PlaceSecondTeamCommand, PlaceAdditionalPlayerCommand,
                      RemoveAllPlayersCommand, RemoveSecondTeamCommand, RemoveAdditionalOffencePlayerCommand,
                      ChangeSecondTeamSymbolsCommand,
                      PlaceFigureCommand, RemoveFigureCommand, RemoveAllFiguresCommand,
                      PlacePencilLinesCommand, RemovePencilLinesCommand,
                      PlaceLabelCommand, RemoveLabelCommand, RemoveAllLabelsCommand,
                      RemoveAllActionsCommand)
from Views.Graphics import Field
from Views import SchemeWidget
from Core.Enums import TeamType
from Views.Dialog_windows import DialogEditScheme
from .player_presenter import PlayerPresenter
from .figure_presenter import FigurePresenter
from .label_presenter import LabelPresenter
from .Mappers import PlayerMapper, FigureMapper, LabelMapper, PencilLineMapper

if TYPE_CHECKING:
    from uuid import UUID
    from PySide6.QtGui import QUndoCommand
    from Core.Enums import PlaybookType, SymbolType
    from PlayCreator_main import PlayCreatorApp
    from View_Models import SchemeModel, PlayerModel, FigureModel, LabelModel, PencilLineModel
    from View_Models.Other import PlaybookModelsFabric, DeletionObserver


class SceneYPoints(NamedTuple):
    top_y: float
    bot_y: float


class SchemePresenter:
    @log_method()
    def __init__(self, scheme_model: 'SchemeModel', view: 'PlayCreatorApp', scheme_view: 'SchemeWidget',
                 playbook_type: 'PlaybookType', playbook_items_fabric: 'PlaybookModelsFabric',
                 deletion_observer: 'DeletionObserver'):
        self._model = scheme_model
        self._view = view
        self._scheme_view = scheme_view
        self._playbook_items_fabric = playbook_items_fabric
        self._deletion_observer = deletion_observer
        self._scene = Field(playbook_type)
        self._undo_stack = QUndoStack(active=True, undoLimit=UNDO_STACK_LIMIT)
        self._first_team_player_mappers: dict['UUID', 'PlayerMapper'] = {}
        self._second_team_player_mappers: dict['UUID', 'PlayerMapper'] = {}
        self._additional_player_mapper: Optional['PlayerMapper'] = None
        self._figure_mappers: dict['UUID', 'FigureMapper'] = {}
        self._pencil_line_mappers: dict['UUID', 'PencilLineMapper'] = {}
        self._label_mappers: dict['UUID', 'LabelMapper'] = {}
        self._connect_signals()

    @log_method()
    def _connect_signals(self) -> None:
        self._undo_stack.canUndoChanged.connect(lambda is_enabled: self._view.set_undo_action_state(is_enabled))
        self._undo_stack.canRedoChanged.connect(lambda is_enabled: self._view.set_redo_action_state(is_enabled))
        self._model.zoomChanged.connect(lambda zoom_value: self._view.set_current_zoom(zoom_value))
        self._model.nameChanged.connect(lambda name: self._scheme_view.setText(name))
        self._model.noteChanged.connect(lambda note: self._scheme_view.setToolTip(note))
        self._model.firstTeamPlayerAdded.connect(self._place_first_team_player)
        self._model.firstTeamPlayersRemoved.connect(self._remove_all_players)
        self._model.firstTeamStateChanged.connect(lambda first_team_type, first_team_position:
                                                  self._view.set_gui_for_first_team(first_team_type, first_team_position))
        self._model.secondTeamPlayerAdded.connect(self._place_second_team_player)
        self._model.secondTeamPlayersRemoved.connect(self._remove_second_team_players)
        self._model.secondTeamStateChanged.connect(lambda second_team_type:
                                                   self._view.set_gui_for_second_team(second_team_type))
        self._model.additionalPlayerAdded.connect(self._place_additional_player)
        self._model.additionalPlayerRemoved.connect(self._remove_additional_player)
        self._scene.figurePainted.connect(self._handle_place_figure)
        self._model.figureAdded.connect(self._place_figure_item)
        self._scene.figureRemoveClicked.connect(self._handle_remove_figure)
        self._model.figureRemoved.connect(self._remove_figure_item)
        self._model.allFiguresRemoved.connect(self._remove_all_figure_items)
        self._scene.pencilPainted.connect(self._handle_place_pencil_lines)
        self._model.pencilLinesAdded.connect(self._place_pencil_line_items)
        self._model.pencilLinesRemoved.connect(self._remove_pencil_lines_items)
        self._model.allPencilLinesRemoved.connect(self._remove_all_pencil_line_items)
        self._scene.labelPlaced.connect(self._handle_place_label)
        self._model.labelAdded.connect(self._place_label_item)
        self._scene.labelRemoveClicked.connect(self._handle_remove_label)
        self._model.labelRemoved.connect(self._remove_label_item)
        self._model.allLabelsRemoved.connect(self._remove_all_label_items)


        self._view.render_signal.connect(lambda: print(f'{self.render_to_bytes() = }'))

    @log_method()
    def _execute_command(self, command: 'QUndoCommand') -> None:
        self._undo_stack.push(command)

    @log_method()
    def clear_undo_stack(self) -> None:
        self._undo_stack.clear()

    @log_method()
    def handle_view_point_changed(self, view_point_x: int, view_point_y: int) -> None:
        self._model.view_point_x = view_point_x
        self._model.view_point_y = view_point_y

    @log_method()
    def handle_zoom_changed(self, zoom_value: int) -> None:
        self._model.zoom = zoom_value

    @log_method()
    def handle_scheme_selected(self) -> None:
        self._view.select_scheme(self._scheme_view, self._scene,
                                 self._model.view_point_x, self._model.view_point_y, self._model.zoom,
                                 self._model.first_team, self._model.second_team,
                                 bool(self._model.additional_player), self._model.first_team_position,
                                 self._undo_stack.canUndo(), self._undo_stack.canRedo())

    @log_method()
    def handle_undo(self) -> None:
        self._undo_stack.undo()

    @log_method()
    def handle_redo(self) -> None:
        self._undo_stack.redo()

    @log_method()
    def handle_edit_scheme(self) -> None:
        dialog_edit_scheme = DialogEditScheme(self._model.name, self._model.note, parent=self._view)
        dialog_edit_scheme.exec()
        if dialog_edit_scheme.result():
            data = dialog_edit_scheme.get_data()
            self._model.name = data.name
            self._model.note = data.note

    @log_method()
    def handle_place_first_team_players(self, team_type: 'TeamType', first_team_position: int) -> None:
        if not self._model.first_team:
            player_models_lst = self._playbook_items_fabric.create_new_first_team_player_models(
                self._model, team_type, first_team_position
            )
            place_first_team_command = PlaceFirstTeamCommand(self._model, player_models_lst, team_type,
                                                             first_team_position)
            self._execute_command(place_first_team_command)

    def _place_first_team_player(self, player_model: 'PlayerModel') -> None:
        player_view = self._scene.place_first_team_player_item(player_model.get_data_for_view())
        player_presenter = PlayerPresenter(self._playbook_items_fabric, self._deletion_observer, self._execute_command,
                                           player_model, self._view, player_view)
        self._first_team_player_mappers[player_model.uuid] = PlayerMapper(player_presenter, player_model, player_view)

    @log_method()
    def handle_remove_all_players(self) -> None:
        if self._model.first_team:
            remove_all_players_command = RemoveAllPlayersCommand(self._deletion_observer, self._model)
            self._execute_command(remove_all_players_command)

    def _remove_all_players(self) -> None:
        self._scene.remove_first_team_player_items()
        self._first_team_player_mappers.clear()

    @log_method()
    def handle_place_second_team_players(self, team_type: 'TeamType') -> None:
        if not self._model.second_team:
            player_models_lst = self._playbook_items_fabric.create_new_second_team_player_models(
                self._model, team_type, self._model.first_team_position
            )
            place_second_team_command = PlaceSecondTeamCommand(self._model, player_models_lst, team_type)
            self._execute_command(place_second_team_command)

    def _place_second_team_player(self, player_model: 'PlayerModel') -> None:
        player_view = self._scene.place_second_team_player_item(player_model.get_data_for_view())
        player_presenter = PlayerPresenter(self._playbook_items_fabric, self._deletion_observer, self._execute_command,
                                           player_model, self._view, player_view)
        self._second_team_player_mappers[player_model.uuid] = PlayerMapper(player_presenter, player_model, player_view)

    @log_method()
    def handle_remove_second_team_players(self) -> None:
        if self._model.second_team:
            remove_second_team_command = RemoveSecondTeamCommand(self._deletion_observer, self._model)
            self._execute_command(remove_second_team_command)

    def _remove_second_team_players(self) -> None:
        self._scene.remove_second_team_player_items()
        self._second_team_player_mappers.clear()

    @log_method()
    def handle_place_additional_player(self) -> None:
        if not self._model.additional_player:
            player_model = self._playbook_items_fabric.create_new_additional_player_model(
                self._model, self._model.first_team_position
            )
            place_additional_player_command = PlaceAdditionalPlayerCommand(self._model, player_model)
            self._execute_command(place_additional_player_command)

    def _place_additional_player(self, player_model: 'PlayerModel') -> None:
        player_view = self._scene.place_additional_player_item(player_model.get_data_for_view())
        player_presenter = PlayerPresenter(self._playbook_items_fabric, self._deletion_observer, self._execute_command,
                                           player_model, self._view, player_view)
        self._additional_player_mapper = PlayerMapper(player_presenter, player_model, player_view)
        self._view.set_gui_for_additional_player(bool(self._model.additional_player))

    @log_method()
    def handle_remove_additional_player(self) -> None:
        if self._model.additional_player:
            remove_additional_player_command = RemoveAdditionalOffencePlayerCommand(self._deletion_observer,
                                                                                    self._model)
            self._execute_command(remove_additional_player_command)

    def _remove_additional_player(self) -> None:
        self._scene.remove_additional_player_item()
        self._additional_player_mapper = None
        self._view.set_gui_for_additional_player(bool(self._model.additional_player))

    @log_method()
    def handle_second_players_symbol_changed(self, new_symbol_type: 'SymbolType') -> None:
        change_second_team_symbols_command = ChangeSecondTeamSymbolsCommand(self._model, new_symbol_type)
        self._execute_command(change_second_team_symbols_command)

    @log_method()
    def _handle_place_figure(self, figure_data: dict) -> None:
        if figure_data['width'] != 0 and figure_data['height'] != 0:
            figure_model = self._playbook_items_fabric.create_figure_model(self._model, **figure_data)
            place_figure_command = PlaceFigureCommand(self._model, figure_model)
            self._execute_command(place_figure_command)

    def _place_figure_item(self, figure_model: 'FigureModel') -> None:
        figure_view = self._scene.place_figure_item(figure_model.get_data_for_view())
        figure_presenter = FigurePresenter(self._execute_command, figure_model, self._view, figure_view)
        self._figure_mappers[figure_model.uuid] = FigureMapper(figure_presenter, figure_model, figure_view)

    @log_method()
    def _handle_remove_figure(self, figure_model_uuid: 'UUID') -> None:
        figure_model = self._figure_mappers[figure_model_uuid].model
        remove_figure_command = RemoveFigureCommand(self._deletion_observer, self._model, figure_model)
        self._execute_command(remove_figure_command)

    def _remove_figure_item(self, figure_model: 'FigureModel') -> None:
        figure_item = self._figure_mappers[figure_model.uuid].view
        self._scene.remove_figure_item(figure_item)
        mapper = self._figure_mappers.pop(figure_model.uuid)

    @log_method()
    def handle_remove_all_figures(self) -> None:
        if self._model.figures:
            remove_all_figures_command = RemoveAllFiguresCommand(self._deletion_observer, self._model)
            self._execute_command(remove_all_figures_command)

    def _remove_all_figure_items(self) -> None:
        self._scene.remove_all_figure_items()
        self._figure_mappers.clear()

    @log_method()
    def _handle_place_pencil_lines(self, pencil_lines_data: list[dict]) -> None:
        pencil_line_models_list = [self._playbook_items_fabric.create_pencil_line_model(self._model, **pencil_line_data)
                                   for pencil_line_data in pencil_lines_data]
        place_pencil_lines_command = PlacePencilLinesCommand(self._model, pencil_line_models_list)
        self._execute_command(place_pencil_lines_command)

    def _place_pencil_line_items(self, pencil_line_models: list['PencilLineModel']) -> None:
        for pencil_line_model in pencil_line_models:
            pencil_line_view = self._scene.place_pencil_line_item(pencil_line_model.get_data_for_view())
            self._pencil_line_mappers[pencil_line_model.uuid] = PencilLineMapper(pencil_line_model, pencil_line_view)

    def _remove_pencil_lines_items(self, pencil_line_models: list['PencilLineModel']) -> None:
        for pencil_line_model in pencil_line_models:
            pencil_line_view = self._pencil_line_mappers[pencil_line_model.uuid].view
            self._scene.remove_pencil_line_item(pencil_line_view)
            mapper = self._pencil_line_mappers.pop(pencil_line_model.uuid)

    @log_method()
    def handle_remove_all_pencil_lines(self) -> None:
        if self._model.pencil_lines:
            remove_pencil_lines_command = RemovePencilLinesCommand(self._deletion_observer, self._model)
            self._execute_command(remove_pencil_lines_command)

    def _remove_all_pencil_line_items(self) -> None:
        self._scene.remove_all_pencil_line_items()
        self._pencil_line_mappers.clear()

    @log_method()
    def _handle_place_label(self, label_data: dict) -> None:
        label_model = self._playbook_items_fabric.create_label_model(self._model, **label_data)
        place_label_command = PlaceLabelCommand(self._model, label_model)
        self._execute_command(place_label_command)

    def _place_label_item(self, label_model: 'LabelModel') -> None:
        label_view = self._scene.place_label_item(label_model.get_data_for_view())
        label_presenter = LabelPresenter(self._execute_command, label_model, self._view, label_view)
        self._label_mappers[label_model.uuid] = LabelMapper(label_presenter, label_model, label_view)

    @log_method()
    def _handle_remove_label(self, label_model_uuid: 'UUID') -> None:
        label_model = self._label_mappers[label_model_uuid].model
        remove_label_command = RemoveLabelCommand(self._deletion_observer, self._model, label_model)
        self._execute_command(remove_label_command)

    def _remove_label_item(self, label_model: 'LabelModel') -> None:
        label_item = self._label_mappers[label_model.uuid].view
        self._scene.remove_label_item(label_item)
        mapper = self._label_mappers.pop(label_model.uuid)

    @log_method()
    def handle_remove_all_labels(self) -> None:
        if self._model.labels:
            remove_labels_command = RemoveAllLabelsCommand(self._deletion_observer, self._model)
            self._execute_command(remove_labels_command)

    def _remove_all_label_items(self) -> None:
        self._scene.remove_all_label_items()
        self._label_mappers.clear()

    @log_method()
    def handle_remove_all_actions(self) -> None:
        remove_all_actions_command = RemoveAllActionsCommand(self._deletion_observer, self._model)
        self._execute_command(remove_all_actions_command)

    @log_method()
    def handle_save_scheme_like_picture(self) -> None:
        save_window = QFileDialog(parent=self._view)
        save_window.setOption(QFileDialog.Option.DontConfirmOverwrite, False)
        filters = 'JPEG (*.jpg *.jpeg *.jpe *.jfif);; TIFF (*.tif *.tiff);; PNG (*.png)'
        file_path, _ = save_window.getSaveFileName(self._view, 'Сохранить как изображение', filter=filters, selectedFilter='PNG (*.png)')
        self.render_picture(file_path, self._get_user_rendering_area())

    def render_picture(self, path: str, rendering_area: Optional['QRect'] = None) -> None:
        if not rendering_area:
            rendering_area = self._get_default_rendering_area()
        base_width = 1000
        img = QImage(base_width, int(base_width * rendering_area.height() / rendering_area.width()), QImage.Format_ARGB8565_Premultiplied)
        img.fill(Qt.white)
        painter = QPainter(img)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform | QPainter.VerticalSubpixelPositioning | QPainter.LosslessImageRendering)
        self._scene.render(painter, source=rendering_area)
        img.save(f'{path}')
        painter.end()

    def render_to_bytes(self) -> 'QByteArray':
        rendering_area = self._get_default_rendering_area()
        base_width = 1000
        img = QImage(base_width, int(base_width * rendering_area.height() / rendering_area.width()), QImage.Format_ARGB8565_Premultiplied)
        painter = QPainter(img)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform | QPainter.VerticalSubpixelPositioning | QPainter.LosslessImageRendering)
        self._scene.render(painter, source=rendering_area)
        painter.end()
        buffer = QBuffer()
        buffer.open(QBuffer.OpenModeFlag.ReadWrite)
        img.save(buffer, 'PNG')
        return buffer.data()

    def _get_user_rendering_area(self) -> 'QRect':
        polygon = self._view.graphics_view.mapToScene(
            QRect(0, 0, self._view.graphics_view.width() - 14, self._view.graphics_view.height() - 13)  # 14 и 13 - отступы из-за скроллбаров
        )
        rect = polygon.boundingRect()
        if rect.x() < 0:
            rect.setWidth(rect.width() + rect.x())
            rect.setX(Config.FieldData.border_style.width() / 2)
        if rect.y() <= 0:
            rect.setHeight(rect.height() + rect.y())
            rect.setY(Config.FieldData.border_style.width() / 2)
        return rect

    def _get_default_rendering_area(self) -> 'QRect':
        extreme_scene_y_points = self._get_extreme_scene_y_points()
        if extreme_scene_y_points:
            return QRect(0, int(extreme_scene_y_points.top_y),
                         int(self._scene.width()), int(extreme_scene_y_points.bot_y - extreme_scene_y_points.top_y))
        return QRect(0, 0, int(self._scene.width()), int(self._scene.height()))

    def _get_extreme_scene_y_points(self) -> Optional['SceneYPoints']:
        top_y, bot_y = float('inf'), - float('inf')
        for player_item in self._scene.first_team_players:
            top_y = min(top_y, player_item.y())
            bot_y = max(bot_y, player_item.y() + player_item.rect.height())
            for action in player_item.actions:
                for action_line in action.action_lines:
                    top_y = min(top_y, action_line.line().y1(), action_line.line().y2())
                    bot_y = max(bot_y, action_line.line().y1(), action_line.line().y2())
        for player_item in self._scene.second_team_players:
            top_y = min(top_y, player_item.y())
            bot_y = max(bot_y, player_item.y() + player_item.rect.height())
            for action in player_item.actions:
                for action_line in action.action_lines:
                    top_y = min(top_y, action_line.line().y1(), action_line.line().y2())
                    bot_y = max(bot_y, action_line.line().y1(), action_line.line().y2())
        if self._scene.additional_player:
            top_y = min(top_y, self._scene.additional_player.y())
            bot_y = max(bot_y, self._scene.additional_player.y() + self._scene.additional_player.rect.height())
            for action in self._scene.additional_player.actions:
                for action_line in action.action_lines:
                    top_y = min(top_y, action_line.line().y1(), action_line.line().y2())
                    bot_y = max(bot_y, action_line.line().y1(), action_line.line().y2())
        for figure_item in self._scene.figures:
            top_y = min(top_y, figure_item.y())
            bot_y = max(bot_y, figure_item.y() + figure_item.rect().height())
        for label_item in self._scene.labels:
            top_y = min(top_y, label_item.y())
            bot_y = max(bot_y, label_item.y() + label_item.rect().height())
        for pencil_line in self._scene.pencil_lines:
            top_y = min(top_y, pencil_line.line().y1(), pencil_line.line().y2())
            bot_y = max(bot_y, pencil_line.line().y1(), pencil_line.line().y2())
        # Ограничение верхней точки сохраняемой области c отступом от крайнего итема верхней границей сцены
        top_y = max(top_y - 30, 0)
        # Ограничение нижней точки сохраняемой области c отступом от крайнего итема нижней границей сцены
        bot_y = min(bot_y + 30, self._scene.sceneRect().height())
        if top_y != float('inf') and bot_y != - float('inf'):
            return SceneYPoints(top_y, bot_y)
        return None
