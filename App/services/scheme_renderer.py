from typing import TYPE_CHECKING, Optional, NamedTuple

from PySide6.QtCore import Qt, QRectF, QRect, QBuffer
from PySide6.QtGui import QImage, QPainter

import Config

if TYPE_CHECKING:
    from PySide6.QtCore import QByteArray
    from Views.Graphics import Field
    from Views import CustomGraphicsView


class SceneYPoints(NamedTuple):
    top_y: float
    bot_y: float


class SchemeRenderer:
    def render_to_picture(self, path: str, scene: 'Field', graphics_view: Optional['CustomGraphicsView']) -> None:
        if not graphics_view:
            rendering_area = self._get_default_rendering_area(scene)
        else:
            rendering_area = self._get_user_rendering_area(graphics_view)
        base_width = 1000
        img = QImage(base_width, int(base_width * rendering_area.height() / rendering_area.width()), QImage.Format_ARGB8565_Premultiplied)
        img.fill(Qt.white)
        painter = QPainter(img)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform | QPainter.VerticalSubpixelPositioning | QPainter.LosslessImageRendering)
        scene.render(painter, source=rendering_area)
        img.save(f'{path}')
        painter.end()

    def render_to_bytes(self, scene: 'Field') -> 'QByteArray':
        rendering_area = self._get_default_rendering_area(scene)
        base_width = 1000
        img = QImage(base_width, int(base_width * rendering_area.height() / rendering_area.width()), QImage.Format_ARGB8565_Premultiplied)
        painter = QPainter(img)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform | QPainter.VerticalSubpixelPositioning | QPainter.LosslessImageRendering)
        scene.render(painter, source=rendering_area)
        painter.end()
        buffer = QBuffer()
        buffer.open(QBuffer.OpenModeFlag.ReadWrite)
        img.save(buffer, 'PNG')
        return buffer.data()

    @staticmethod
    def _get_user_rendering_area(graphics_view: 'CustomGraphicsView') -> 'QRectF':
        polygon = graphics_view.mapToScene(
            QRect(0, 0, graphics_view.width() - 14, graphics_view.height() - 13)  # 14 и 13 - отступы из-за скроллбаров
        )
        rect = polygon.boundingRect()
        if rect.x() < 0:
            rect.setWidth(rect.width() + rect.x())
            rect.setX(Config.FieldData.border_style.width() / 2)
        if rect.y() <= 0:
            rect.setHeight(rect.height() + rect.y())
            rect.setY(Config.FieldData.border_style.width() / 2)
        return rect

    def _get_default_rendering_area(self, scene: 'Field') -> 'QRect':
        extreme_scene_y_points = self._get_extreme_scene_y_points(scene)
        if extreme_scene_y_points:
            return QRect(0, int(extreme_scene_y_points.top_y),
                         int(scene.width()), int(extreme_scene_y_points.bot_y - extreme_scene_y_points.top_y))
        return QRect(0, 0, int(scene.width()), int(scene.height()))

    @staticmethod
    def _get_extreme_scene_y_points(scene: 'Field') -> Optional['SceneYPoints']:
        top_y, bot_y = float('inf'), - float('inf')
        for player_item in scene.first_team_players:
            top_y = min(top_y, player_item.y())
            bot_y = max(bot_y, player_item.y() + player_item.rect.height())
            for action in player_item.actions:
                for action_line in action.action_lines:
                    top_y = min(top_y, action_line.line().y1(), action_line.line().y2())
                    bot_y = max(bot_y, action_line.line().y1(), action_line.line().y2())
        for player_item in scene.second_team_players:
            top_y = min(top_y, player_item.y())
            bot_y = max(bot_y, player_item.y() + player_item.rect.height())
            for action in player_item.actions:
                for action_line in action.action_lines:
                    top_y = min(top_y, action_line.line().y1(), action_line.line().y2())
                    bot_y = max(bot_y, action_line.line().y1(), action_line.line().y2())
        if scene.additional_player:
            top_y = min(top_y, scene.additional_player.y())
            bot_y = max(bot_y, scene.additional_player.y() + scene.additional_player.rect.height())
            for action in scene.additional_player.actions:
                for action_line in action.action_lines:
                    top_y = min(top_y, action_line.line().y1(), action_line.line().y2())
                    bot_y = max(bot_y, action_line.line().y1(), action_line.line().y2())
        for figure_item in scene.figures:
            top_y = min(top_y, figure_item.y())
            bot_y = max(bot_y, figure_item.y() + figure_item.rect().height())
        for label_item in scene.labels:
            top_y = min(top_y, label_item.y())
            bot_y = max(bot_y, label_item.y() + label_item.rect().height())
        for pencil_line in scene.pencil_lines:
            top_y = min(top_y, pencil_line.line().y1(), pencil_line.line().y2())
            bot_y = max(bot_y, pencil_line.line().y1(), pencil_line.line().y2())
        # Ограничение верхней точки сохраняемой области c отступом от крайнего итема верхней границей сцены
        top_y = max(top_y - 30, 0)
        # Ограничение нижней точки сохраняемой области c отступом от крайнего итема нижней границей сцены
        bot_y = min(bot_y + 30, scene.sceneRect().height())
        if top_y != float('inf') and bot_y != - float('inf'):
            return SceneYPoints(top_y, bot_y)
        return None