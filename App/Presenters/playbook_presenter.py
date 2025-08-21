import os.path
from typing import TYPE_CHECKING, Optional

from PySide6.QtWidgets import QFileDialog

import Config
from View_Models import PlaybookModel, SchemeModel
from Views.Dialog_windows import DialogEditPlaybook, DialogProgressBar, DialogInfo, DialogInput
from .scheme_presenter import SchemePresenter
from .Mappers import SchemeMapper

if TYPE_CHECKING:
    from uuid import UUID
    from Core.Enums import TeamType, SymbolType
    from View_Models.Other import PlaybookModelsFabric, DeletionObserver
    from PlayCreator_main import PlayCreatorApp
    from Services.Local_DB.Repositories.playbook_manager import PlaybookManager

__all__ = ('PlaybookPresenter', )


class PlaybookPresenter:
    def __init__(self, model: 'PlaybookModel', view: 'PlayCreatorApp', playbook_items_fabric: 'PlaybookModelsFabric',
                 deletion_observer: 'DeletionObserver'):
        self._view = view
        self._model = model
        self._playbook_items_fabric = playbook_items_fabric
        self._deletion_observer = deletion_observer
        self._scheme_mappers: dict['UUID', 'SchemeMapper'] = {}
        self._selected_scheme_presenter: Optional['SchemePresenter'] = None
        self._connect_signals()

    def _connect_signals(self) -> None:
        self._model.nameChanged.connect(lambda name: self._view.update_playbook_name(name))
        self._model.infoChanged.connect(lambda info: self._view.update_playbook_info(info))
        self._model.schemeAdded.connect(self._add_scheme_item)
        self._model.schemeRemoved.connect(self._remove_scheme_widget)
        self._model.schemeMoved.connect(self._move_scheme_widget)

    def handle_edit_playbook(self) -> None:
        dialog_edit_playbook = DialogEditPlaybook(self._model.name, self._model.info,
                                                  who_can_edit=self._model.who_can_edit,
                                                  who_can_see=self._model.who_can_see,
                                                  parent=self._view)
        dialog_edit_playbook.exec()
        if dialog_edit_playbook.result():
            data = dialog_edit_playbook.get_data()
            self._model.name = data.name
            self._model.info = data.info
            self._model.who_can_edit = data.who_can_edit
            self._model.who_can_see = data.who_can_see

    def handle_add_scheme(self) -> None:
        scheme_model = self._playbook_items_fabric.create_scheme_model(
            self._model, 'Новая схема',
            getattr(Config, f'{self._model.playbook_type.name}_field_data'.lower()).width / 2,
            getattr(Config, f'{self._model.playbook_type.name}_field_data'.lower()).length / 2,
        )
        self._model.add_scheme(scheme_model)

    def _add_scheme_item(self, scheme_model: 'SchemeModel') -> None:
        scheme_view = self._view.add_scheme_widget(scheme_model.uuid, scheme_model.name, scheme_model.note)
        scheme_presenter = SchemePresenter(scheme_model, self._view, scheme_view, self._model.playbook_type,
                                           self._playbook_items_fabric, self._deletion_observer)
        self._scheme_mappers[scheme_model.uuid] = SchemeMapper(scheme_presenter, scheme_model, scheme_view)
        self.transfer_to_scheme_presenter_select_scheme(scheme_model.uuid)

    def transfer_to_scheme_presenter_select_scheme(self, model_uuid: 'UUID') -> None:
        self._selected_scheme_presenter = self._scheme_mappers[model_uuid].presenter
        self._selected_scheme_presenter.handle_scheme_selected()

    def handle_remove_scheme(self, model_uuid: 'UUID') -> None:
        scheme_model = self._scheme_mappers[model_uuid].model
        self._model.remove_scheme(scheme_model)

    def _remove_scheme_widget(self, scheme_model: 'SchemeModel') -> None:
        scheme_widget = self._scheme_mappers[scheme_model.uuid].view
        self._view.remove_scheme_widget(scheme_widget)
        if scheme_widget == self._view.selected_scheme and \
                self._view.listWidget_schemes.count() > 0:
            self.transfer_to_scheme_presenter_select_scheme(self._view.listWidget_schemes.currentItem().model_uuid)
        mapper = self._scheme_mappers.pop(scheme_model.uuid)
        del mapper.model
        del mapper.presenter
        del mapper.view
        del mapper

    def handle_move_up_scheme(self, model_uuid: 'UUID', view_index: int) -> None:
        scheme_model = self._scheme_mappers[model_uuid].model
        self._model.move_up_scheme(view_index, scheme_model)

    def handle_move_down_scheme(self, model_uuid: 'UUID', view_index: int) -> None:
        scheme_model = self._scheme_mappers[model_uuid].model
        self._model.move_down_scheme(view_index, scheme_model)

    def _move_scheme_widget(self, last_index: int, new_index: int) -> None:
        self._view.move_scheme_widget(last_index, new_index)

    def handle_save_all_schemes_like_picture(self) -> None:
        dir_path = QFileDialog.getExistingDirectory(parent=self._view, caption='Укажите путь для сохранения схем')
        if dir_path:
            for scheme_mapper in self._scheme_mappers.values():
                scheme_name = scheme_mapper.model.name
                scheme_presenter = scheme_mapper.presenter
                file_name = self._get_valid_file_name(scheme_name)
                file_path = f'{dir_path}/{file_name}.png'
                counter = 1
                while os.path.exists(file_path):
                    file_path = f'{dir_path}/Новая схема-{counter}.png'
                    counter += 1
                scheme_presenter.render_picture(file_path)

    def _get_valid_file_name(self, scheme_name: str) -> str:
        file_name = f'{scheme_name}'
        invalid_chars = r'/\:*?"<>|'
        for char in invalid_chars:
            file_name = file_name.replace(char, '_')
        return file_name.strip()

    def handle_save_playbook_local(self, playbook_manager: 'PlaybookManager') -> None:
        dialog_progress = DialogProgressBar(parent=self._view, operation_name='Сохранение плейбука')
        dialog_progress.show()
        try:
            playbook_manager.save(self._model, is_new_playbook=False, set_progress_func=dialog_progress.set_progress_value)
            self._model.reset_changed_flag()
            for scheme_mapper in self._scheme_mappers.values():
                scheme_mapper.presenter.clear_undo_stack()
        except Exception as e:
            dialog_progress.hide()
            dialog_info = DialogInfo('Ошибка', 'Произошла ошибка. Плейбук не был сохранён.', check_box=False,
                                     decline_button=False, accept_button_text='Ок', parent=self._view)
            dialog_info.exec()
            raise e
        finally:
            dialog_progress.finish()

    def handle_save_playbook_local_as(self, playbook_manager: 'PlaybookManager') -> None:
        dialog_input = DialogInput('Сохранить как', 'Введите название плейбука:', parent=self._view)
        dialog_input.exec()
        if dialog_input.result():
            self._model.name = dialog_input.get_data().text
            self._model.set_new_uuid_for_all_items()
            dialog_progress = DialogProgressBar(self._view, 'Сохранение плейбука')
            dialog_progress.show()
            try:
                playbook_manager.save(self._model, is_new_playbook=True, set_progress_func=dialog_progress.set_progress_value)
                self._model.reset_changed_flag()
                for scheme_mapper in self._scheme_mappers.values():
                    scheme_mapper.presenter.clear_undo_stack()
            except Exception as e:
                dialog_progress.hide()
                dialog_info = DialogInfo('Ошибка', 'Произошла ошибка. Плейбук не был сохранён.', check_box=False,
                                         decline_button=False, accept_button_text='Ок', parent=self._view)
                dialog_info.exec()
                raise e
            finally:
                dialog_progress.finish()

    def transfer_to_scheme_presenter_handle_action_undo_clicked(self) -> None:
        self._selected_scheme_presenter.handle_undo()

    def transfer_to_scheme_presenter_handle_action_redo_clicked(self) -> None:
        self._selected_scheme_presenter.handle_redo()

    def transfer_to_scheme_presenter_handle_view_point_changed(self, view_point_x: int, view_point_y: int) -> None:
        self._selected_scheme_presenter.handle_view_point_changed(view_point_x, view_point_y)

    def transfer_to_scheme_presenter_handle_zoom_changed(self, zoom_value: int) -> None:
        self._selected_scheme_presenter.handle_zoom_changed(zoom_value)

    def transfer_to_scheme_presenter_handle_edit_scheme_clicked(self, model_uuid: 'UUID') -> None:
        self._scheme_mappers[model_uuid].presenter.handle_edit_scheme()

    def transfer_to_scheme_presenter_handle_place_first_team_clicked(self, team_type: 'TeamType', first_team_position: int) -> None:
        self._selected_scheme_presenter.handle_place_first_team_players(team_type, first_team_position)

    def transfer_to_scheme_presenter_handle_place_second_team_clicked(self, team_type: 'TeamType') -> None:
        self._selected_scheme_presenter.handle_place_second_team_players(team_type)

    def transfer_to_scheme_presenter_handle_place_additional_player_clicked(self) -> None:
        self._selected_scheme_presenter.handle_place_additional_player()

    def transfer_to_scheme_presenter_handle_remove_all_players_clicked(self) -> None:
        self._selected_scheme_presenter.handle_remove_all_players()

    def transfer_to_scheme_presenter_handle_remove_second_team_clicked(self) -> None:
        self._selected_scheme_presenter.handle_remove_second_team_players()

    def transfer_to_scheme_presenter_handle_remove_additional_player_clicked(self) -> None:
        self._selected_scheme_presenter.handle_remove_additional_player()

    def transfer_to_scheme_presenter_second_players_symbol_changed(self, new_symbol_type: 'SymbolType') -> None:
        self._selected_scheme_presenter.handle_second_players_symbol_changed(new_symbol_type)

    def transfer_to_scheme_presenter_remove_figures_clicked(self) -> None:
        self._selected_scheme_presenter.handle_remove_all_figures()

    def transfer_to_scheme_presenter_remove_pencil_lines_clicked(self) -> None:
        self._selected_scheme_presenter.handle_remove_all_pencil_lines()

    def transfer_to_scheme_presenter_remove_labels_clicked(self) -> None:
        self._selected_scheme_presenter.handle_remove_all_labels()

    def transfer_to_scheme_presenter_remove_actions_clicked(self) -> None:
        self._selected_scheme_presenter.handle_remove_all_actions()

    def transfer_to_scheme_presenter_save_like_picture(self) -> None:
        self._selected_scheme_presenter.handle_save_scheme_like_picture()

