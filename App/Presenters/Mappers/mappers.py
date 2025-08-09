from typing import TYPE_CHECKING, Union, Generic, TypeVar

if TYPE_CHECKING:
    from Presenters.scheme_presenter import SchemePresenter
    from Presenters.player_presenter import PlayerPresenter
    from Presenters.figure_presenter import FigurePresenter
    from Presenters.label_presenter import LabelPresenter
    from Presenters.action_presenter import ActionPresenter
    from Models import SchemeModel, PlayerModel, FigureModel, LabelModel, PencilLineModel, ActionModel,\
        ActionLineModel, FinalActionModel
    from Views.Graphics import FirstTeamPlayerView, SecondTeamPlayerView, RectangleView, EllipseView, ProxyWidgetLabel,\
        PencilLineView, ActionView, ActionLineView, FinalActionRouteView, FinalActionBlockView
    from Views import SchemeWidget

__all__ = ('SchemeMapper', 'FigureMapper', 'LabelMapper', 'PencilLineMapper', 'PlayerMapper',
           'ActionMapper', 'ActionPartsMapper')


T_Presenter = TypeVar('T_Presenter')
T_Model = TypeVar('T_Model')
T_View = TypeVar('T_View')


class BaseMapper(Generic[T_Model, T_View]):
    def __init__(self, model: 'T_Model', view: 'T_View'):
        self.model = model
        self.view = view


class PresenterMixin(Generic[T_Presenter]):
    def __init__(self, presenter: 'T_Presenter'):
        self.presenter = presenter


class SchemeMapper(BaseMapper['SchemeModel', 'SchemeWidget'], PresenterMixin['SchemePresenter']):
    def __init__(self, presenter: 'SchemePresenter', model: 'SchemeModel', view: 'SchemeWidget'):
        BaseMapper.__init__(self, model, view)
        PresenterMixin.__init__(self, presenter)


class PlayerMapper(BaseMapper['PlayerModel', Union['FirstTeamPlayerView', 'SecondTeamPlayerView']], PresenterMixin['PlayerPresenter']):
    def __init__(self, presenter: 'PlayerPresenter', model: 'PlayerModel', view: Union[
        'FirstTeamPlayerView', 'SecondTeamPlayerView']):
        BaseMapper.__init__(self, model, view)
        PresenterMixin.__init__(self, presenter)


class FigureMapper(BaseMapper['FigureModel', Union['Rectangle', 'EllipseView']], PresenterMixin['FigurePresenter']):
    def __init__(self, presenter: 'FigurePresenter', model: 'FigureModel', view: Union['RectangleView', 'EllipseView']):
        BaseMapper.__init__(self, model, view)
        PresenterMixin.__init__(self, presenter)


class LabelMapper(BaseMapper['LabelModel', 'ProxyWidgetLabel'], PresenterMixin['LabelPresenter']):
    def __init__(self, presenter: 'LabelPresenter', model: 'LabelModel', view: 'ProxyWidgetLabel'):
        BaseMapper.__init__(self, model, view)
        PresenterMixin.__init__(self, presenter)


class PencilLineMapper(BaseMapper['PencilLineModel', 'PencilLineView']):
    def __init__(self, model: 'PencilLineModel', view: 'PencilLineView'):
        BaseMapper.__init__(self, model, view)


class ActionMapper(BaseMapper['ActionModel', 'ActionView'], PresenterMixin['ActionPresenter']):
    def __init__(self, presenter: 'ActionPresenter', model: 'ActionModel', view: 'ActionView'):
        BaseMapper.__init__(self, model, view)
        PresenterMixin.__init__(self, presenter)


class ActionPartsMapper(BaseMapper[Union['ActionModel', 'FinalActionModel'],
                                   Union['ActionLineView', 'FinalActionRouteView', 'FinalActionBlockView']]):
    def __init__(self, model: Union['ActionLineModel', 'FinalActionModel'],
                 view: Union['ActionLineView', 'FinalActionRouteView', 'FinalActionBlockView']):
        BaseMapper.__init__(self, model, view)
