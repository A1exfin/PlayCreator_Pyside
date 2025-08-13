from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import Qt

from Config.Enums import AppTheme, TeamType
from Views.Dialog_windows import DialogInfo, DialogAbout, DialogNewPlaybook, DialogOpenPlaybook
from Models import PlaybookModel, SchemeModel, FigureModel, LabelModel, PencilLineModel, PlayerModel, ActionModel,\
    ActionLineModel, FinalActionModel
from .playbook_presenter import PlaybookPresenter
from services.Local_DB.repository.playbook_repository import PlaybookManager
from services.Local_DB import get_session

if TYPE_CHECKING:
    from uuid import UUID
    from Models import MainWindowModel
    from PlayCreator_main import PlayCreatorApp
    from services.Local_DB.DTO.input_DTO import PlaybookInputDTO
    from Config.Enums import SymbolType


__all__ = ('MainWindowPresenter', )


class MainWindowPresenter:
    def __init__(self):
        self._model: Optional['MainWindowModel'] = None
        self._view: Optional['PlayCreatorApp'] = None
        self._playbook_presenter: Optional['PlaybookPresenter'] = None
        self._playbook_manager = PlaybookManager(next(get_session()))

    def set_model_and_view(self, model: 'MainWindowModel', view: 'PlayCreatorApp') -> None:
        self._model = model
        self._connect_model_signals(model)
        self._view = view
        self._connect_view_signals(view)
        self._set_initial_window_state()

    def _connect_model_signals(self, model: 'MainWindowModel') -> None:
        model.modelChanged.connect(self._update_window)
        model.playbookInstalled.connect(self._install_playbook)

    def _connect_view_signals(self, view: 'PlayCreatorApp') -> None:
        view.graphics_view.viewPointChanged.connect(self._transfer_to_playbook_presenter_view_point_changed)
        view.graphics_view.zoomChanged.connect(self._transfer_to_playbook_presenter_zoom_changed)

        view.toolBarAreaChanged.connect(self._handle_tool_bar_area_changed)
        view.action_close_app.triggered.connect(view.close)
        view.action_dark_theme.triggered.connect(self._handle_dark_theme)
        view.action_light_theme.triggered.connect(self._handle_light_theme)
        view.action_presentation_mode.triggered.connect(self._handle_presentation_mode)
        view.action_toolbar_visible.triggered.connect(self._handle_tool_bar_visible)
        view.action_show_remove_scheme_dialog.triggered.connect(self._handle_show_remove_scheme_dialog)
        view.action_show_close_app_dialog.triggered.connect(self._handle_show_close_app_dialog)
        view.action_about.triggered.connect(self._handle_about)
        view.action_new_playbook.triggered.connect(self._handle_create_new_playbook)
        view.action_undo.triggered.connect(self._transfer_to_playbook_presenter_action_undo_clicked)
        view.action_redo.triggered.connect(self._transfer_to_playbook_presenter_action_redo_clicked)
        view.action_save_like_picture.triggered.connect(self._transfer_to_playbook_presenter_save_like_picture)
        view.action_save_all_like_picture.triggered.connect(self._transfer_to_playbook_presenter_save_all_like_picture)
        view.action_save_playbook_local.triggered.connect(self._transfer_to_playbook_presenter_save_playbook_local)
        view.action_save_playbook_local_as.triggered.connect(self._transfer_to_playbook_presenter_save_playbook_local_as)
        view.action_open_local_playbook.triggered.connect(self._handle_open_playbook_local)

        view.pushButton_add_scheme.clicked.connect(self._transfer_to_playbook_presenter_add_scheme_clicked)
        view.schemeItemDoubleClicked.connect(self._transfer_to_playbook_presenter_select_scheme_clicked)
        view.pushButton_edit_playbook.clicked.connect(self._transfer_to_playbook_presenter_edit_playbook_clicked)
        view.removeSchemeBtnClicked.connect(self._transfer_to_playbook_presenter_remove_scheme_clicked)
        view.moveUpSchemeBtnClicked.connect(self._transfer_to_playbook_presenter_move_up_scheme_clicked)
        view.moveDownSchemeBtnClicked.connect(self._transfer_to_playbook_presenter_move_down_scheme_clicked)

        view.editSchemeClicked.connect(self._transfer_to_playbook_presenter_edit_scheme_clicked)
        view.placeFirstTeamClicked.connect(self._transfer_to_playbook_presenter_place_first_team_clicked)
        view.placeSecondTeamClicked.connect(self._transfer_to_playbook_presenter_place_second_team_clicked)
        view.placeAdditionalPlayerClicked.connect(self._transfer_to_playbook_presenter_place_additional_player_clicked)
        view.pushButton_remove_second_team.clicked.connect(self._transfer_to_playbook_presenter_remove_second_team_clicked)
        view.pushButton_del_additional_off_player.clicked.connect(self._transfer_to_playbook_presenter_remove_additional_player_clicked)
        view.pushButton_remove_all_players.clicked.connect(self._transfer_to_playbook_presenter_remove_all_players_clicked)
        view.secondTeamSymbolChanged.connect(self._transfer_to_playbook_presenter_second_players_symbol_changed)

        view.pushButton_remove_figures.clicked.connect(self._transfer_to_playbook_presenter_remove_figures_clicked)
        view.pushButton_remove_pencil.clicked.connect(self._transfer_to_playbook_presenter_remove_pencil_lines_clicked)
        view.pushButton_remove_labels.clicked.connect(self._transfer_to_playbook_presenter_remove_labels_clicked)
        view.pushButton_remove_actions.clicked.connect(self._transfer_to_playbook_presenter_remove_actions_clicked)

    def _set_initial_window_state(self) -> None:
        self._view.set_initial_window_state(self._model.x, self._model.y, self._model.width, self._model.height,
                                            self._model.theme, self._model.is_maximized, self._model.tool_bar_visible,
                                            self._model.tool_bar_area, self._model.presentation_mode,
                                            self._model.show_remove_scheme_dialog, self._model.show_close_app_dialog)

    def handle_move(self, x: int, y: int) -> None:
        self._model.x, self._model.y = x, y

    def handle_resize(self, width: int, height: int) -> None:
        self._model.width, self._model.height = width, height

    def handle_maximized_changed(self, is_maximized: bool) -> None:
        self._model.is_maximized = is_maximized

    def _handle_tool_bar_area_changed(self, tool_bar_area: 'Qt.ToolBarArea') -> None:
        self._model.tool_bar_area = tool_bar_area

    def _handle_dark_theme(self) -> None:
        self._model.theme = AppTheme.DARK
        self._model.about_ico_path = f'://themes/dark_theme/tactic.png'

    def _handle_light_theme(self) -> None:
        self._model.theme = AppTheme.LIGHT
        self._model.about_ico_path = f'://themes/light_theme/tactic.png'

    def _handle_tool_bar_visible(self, visible: bool) -> None:
        self._model.tool_bar_visible = visible

    def _handle_show_remove_scheme_dialog(self, checked: bool) -> None:
        self._model.show_remove_scheme_dialog = checked

    def _handle_show_close_app_dialog(self, checked: bool) -> None:
        self._model.show_close_app_dialog = checked

    def _handle_presentation_mode(self, checked: bool) -> None:
        self._model.presentation_mode = checked

    def _update_window(self, model: 'MainWindowModel') -> None:
        self._view.update_window(model.theme, model.tool_bar_visible, model.presentation_mode,
                                 model.show_remove_scheme_dialog, model.show_close_app_dialog)

    def _handle_about(self) -> None:
        dialog = DialogAbout(self._model.version, self._model.about_ico_path, parent=self._view)
        dialog.exec()

    def handle_close_app(self) -> bool:
        if self._model.show_close_app_dialog:
            dialog_close_app = DialogInfo('Выход', 'Вы уверены что хотите закрыть приложение?', parent=self._view)
            dialog_close_app.exec()
            if dialog_close_app.result():
                if dialog_close_app.check_box_dont_ask_again.checkState() == Qt.CheckState.Checked:
                    self._model.show_close_app_dialog = False
                self._model.save_window_state()
                return True
            return False
        self._model.save_window_state()
        return True

    def _handle_create_new_playbook(self) -> None:
        dialog_new_playbook = DialogNewPlaybook(self._view)
        dialog_new_playbook.exec()
        if dialog_new_playbook.result():
            data = dialog_new_playbook.get_data()
            if data.name != '':
                playbook_model = PlaybookModel(data.name, data.playbook_type)
                self._model.playbook = playbook_model
            else:
                dialog_info = DialogInfo('Некорректное название плейбука', 'Введите корректное название плейбука.',
                                         self._view, False, False, 'ОК')
                dialog_info.exec()

    def _install_playbook(self, playbook_model: 'PlaybookModel') -> None:
        playbook_presenter = PlaybookPresenter(playbook_model, self._view)
        self._playbook_presenter = playbook_presenter
        self._view.set_playbook(playbook_model.name, playbook_model.playbook_type, playbook_model.info)

    def _handle_open_playbook_local(self) -> None:
        local_playbooks_info = self._playbook_manager.get_all_obj_info()
        dialog_open_local_playbook = DialogOpenPlaybook(local_playbooks_info, self._playbook_manager.delete_by_id, parent=self._view)
        dialog_open_local_playbook.exec()
        if dialog_open_local_playbook.result():
            data = dialog_open_local_playbook.get_data()
            playbook_dto = self._playbook_manager.get_by_id(data.selected_playbook_id)
            self._parse_playbook_dto_to_models(playbook_dto)

    def _parse_playbook_dto_to_models(self, playbook_dto: 'PlaybookInputDTO') -> None:
        playbook_model = PlaybookModel(**playbook_dto.model_dump(exclude={'id', 'schemes'}), id_local_db=playbook_dto.id)
        self._model.playbook = playbook_model
        for scheme_dto in playbook_dto.schemes:
            scheme_model = SchemeModel(
                **scheme_dto.model_dump(exclude={'id', 'row_index', 'figures', 'labels', 'pencil_lines', 'players'}),
                id_local_db=scheme_dto.id, add_deleted_item_ids_func=playbook_model.add_deleted_ids
            )
            playbook_model.add_scheme(scheme_model, scheme_dto.row_index)
            for figure_dto in scheme_dto.figures:
                figure_model = FigureModel(**figure_dto.model_dump(exclude={'id'}), id_local_db=figure_dto.id)
                scheme_model.add_figure(figure_model)
            for label_dto in scheme_dto.labels:
                label_model = LabelModel(**label_dto.model_dump(exclude={'id'}), id_local_db=label_dto.id)
                scheme_model.add_label(label_model)
            for pencil_line_dto in scheme_dto.pencil_lines:
                pencil_lines_lst = []
                pencil_line_model = PencilLineModel(**pencil_line_dto.model_dump(exclude={'id'}), id_local_db=pencil_line_dto.id)
                pencil_lines_lst.append(pencil_line_model)
                scheme_model.add_pencil_lines(pencil_lines_lst)
            for player_dto in scheme_dto.players:
                player_model = PlayerModel(
                    **player_dto.model_dump(exclude={'id', 'actions'}),
                    id_local_db=playbook_dto.id, add_deleted_item_ids_func=playbook_model.add_deleted_ids
                )
                if player_model.team_type in (TeamType.OFFENCE, TeamType.KICKOFF, TeamType.PUNT, TeamType.FIELD_GOAL_OFF):
                    scheme_model.add_first_team_players([player_model], scheme_dto.first_team, scheme_dto.first_team_position)
                if player_model.team_type in (TeamType.DEFENCE, TeamType.KICK_RET, TeamType.PUNT_RET, TeamType.FIELD_GOAL_DEF):
                    scheme_model.add_second_team_players([player_model], scheme_dto.second_team)
                if player_model.team_type is TeamType.OFFENCE_ADD:
                    scheme_model.additional_player = player_model
                for action_dto in player_dto.actions:
                    action_lines_lst = []
                    final_actions_lst = []
                    action_model = ActionModel(**action_dto.model_dump(exclude={'id', 'action_lines', 'final_actions'}),
                                               id_local_db=action_dto.id)
                    player_model.add_action(action_model)
                    # print(f'{action_dto.action_lines = }')
                    for action_line_dto in action_dto.action_lines:
                        action_line_model = ActionLineModel(**action_line_dto.model_dump(exclude={'id'}))
                        action_lines_lst.append(action_line_model)
                    for final_action_dto in action_dto.final_actions:
                        final_action_model = FinalActionModel(**final_action_dto.model_dump(exclude={'id'}))
                        final_actions_lst.append(final_action_model)
                    action_model.add_action_parts(action_lines_lst, final_actions_lst)

        # print(f'{playbook_model = }')


    def _transfer_to_playbook_presenter_save_playbook_local(self) -> None:
        self._playbook_presenter.handle_save_playbook_local(self._playbook_manager)

    def _transfer_to_playbook_presenter_save_playbook_local_as(self) -> None:
        self._playbook_presenter.handle_save_playbook_local_as(self._playbook_manager)



    def _transfer_to_playbook_presenter_add_scheme_clicked(self) -> None:
        self._playbook_presenter.handle_add_scheme()

    def _transfer_to_playbook_presenter_select_scheme_clicked(self, model_uuid: 'UUID') -> None:
        self._playbook_presenter.transfer_to_scheme_presenter_select_scheme(model_uuid)

    def _transfer_to_playbook_presenter_edit_playbook_clicked(self) -> None:
        self._playbook_presenter.handle_edit_playbook()

    def _transfer_to_playbook_presenter_view_point_changed(self, view_point_x: int, view_point_y: int) -> None:
        self._playbook_presenter.transfer_to_scheme_presenter_handle_view_point_changed(view_point_x, view_point_y)

    def _transfer_to_playbook_presenter_zoom_changed(self, zoom_value: int) -> None:
        self._playbook_presenter.transfer_to_scheme_presenter_handle_zoom_changed(zoom_value)

    def _transfer_to_playbook_presenter_remove_scheme_clicked(self, model_uuid: 'UUID', scheme_name: str) -> None:
        if self._model.show_remove_scheme_dialog:
            dialog_remove_scheme = DialogInfo('Удаление схемы',
                                              f'Вы уверены что хотите удалить схему "{scheme_name}"?',
                                              parent=self._view)
            dialog_remove_scheme.exec()
            if dialog_remove_scheme.result():
                if dialog_remove_scheme.check_box_dont_ask_again.checkState() == Qt.CheckState.Checked:
                    self._model.show_remove_scheme_dialog = False
                self._playbook_presenter.handle_remove_scheme(model_uuid)
                return
            return
        self._playbook_presenter.handle_remove_scheme(model_uuid)

    def _transfer_to_playbook_presenter_move_up_scheme_clicked(self, model_uuid: 'UUID', scheme_widget_index: int) -> None:
        self._playbook_presenter.handle_move_up_scheme(model_uuid, scheme_widget_index)

    def _transfer_to_playbook_presenter_move_down_scheme_clicked(self, model_uuid: 'UUID', scheme_widget_index: int) -> None:
        self._playbook_presenter.handle_move_down_scheme(model_uuid, scheme_widget_index)

    def _transfer_to_playbook_presenter_edit_scheme_clicked(self, model_uuid: 'UUID') -> None:
        self._playbook_presenter.transfer_to_scheme_presenter_handle_edit_scheme_clicked(model_uuid)

    def _transfer_to_playbook_presenter_action_undo_clicked(self) -> None:
        self._playbook_presenter.transfer_to_scheme_presenter_handle_action_undo_clicked()

    def _transfer_to_playbook_presenter_action_redo_clicked(self) -> None:
        self._playbook_presenter.transfer_to_scheme_presenter_handle_action_redo_clicked()

    def _transfer_to_playbook_presenter_place_first_team_clicked(self, team_type: 'TeamType', first_team_position: int) -> None:
        self._playbook_presenter.transfer_to_scheme_presenter_handle_place_first_team_clicked(team_type, first_team_position)

    def _transfer_to_playbook_presenter_place_second_team_clicked(self, team_type: 'TeamType') -> None:
        self._playbook_presenter.transfer_to_scheme_presenter_handle_place_second_team_clicked(team_type)

    def _transfer_to_playbook_presenter_place_additional_player_clicked(self) -> None:
        self._playbook_presenter.transfer_to_scheme_presenter_handle_place_additional_player_clicked()

    def _transfer_to_playbook_presenter_remove_all_players_clicked(self) -> None:
        self._playbook_presenter.transfer_to_scheme_presenter_handle_remove_all_players_clicked()

    def _transfer_to_playbook_presenter_remove_second_team_clicked(self) -> None:
        self._playbook_presenter.transfer_to_scheme_presenter_handle_remove_second_team_clicked()

    def _transfer_to_playbook_presenter_remove_additional_player_clicked(self) -> None:
        self._playbook_presenter.transfer_to_scheme_presenter_handle_remove_additional_player_clicked()

    def _transfer_to_playbook_presenter_second_players_symbol_changed(self, new_symbol_type: 'SymbolType') -> None:
        self._playbook_presenter.transfer_to_scheme_presenter_second_players_symbol_changed(new_symbol_type)

    def _transfer_to_playbook_presenter_remove_figures_clicked(self) -> None:
        self._playbook_presenter.transfer_to_scheme_presenter_remove_figures_clicked()

    def _transfer_to_playbook_presenter_remove_pencil_lines_clicked(self) -> None:
        self._playbook_presenter.transfer_to_scheme_presenter_remove_pencil_lines_clicked()

    def _transfer_to_playbook_presenter_remove_labels_clicked(self) -> None:
        self._playbook_presenter.transfer_to_scheme_presenter_remove_labels_clicked()

    def _transfer_to_playbook_presenter_remove_actions_clicked(self) -> None:
        self._playbook_presenter.transfer_to_scheme_presenter_remove_actions_clicked()

    def _transfer_to_playbook_presenter_save_like_picture(self) -> None:
        self._playbook_presenter.transfer_to_scheme_presenter_save_like_picture()

    def _transfer_to_playbook_presenter_save_all_like_picture(self) -> None:
        self._playbook_presenter.handle_save_all_schemes_like_picture()