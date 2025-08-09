from .scheme_commands import PlaceFirstTeamCommand, PlaceSecondTeamCommand, RemoveSecondTeamCommand,\
    PlaceAdditionalPlayerCommand, RemoveAdditionalOffencePlayerCommand, RemoveAllPlayersCommand, PlaceFigureCommand,\
    RemoveFigureCommand, RemoveAllFiguresCommand, PlacePencilLinesCommand, RemovePencilLinesCommand, PlaceLabelCommand,\
    RemoveLabelCommand, RemoveAllLabelsCommand, ChangeSecondTeamSymbolsCommand, RemoveAllActionsCommand
from .player_commands import MovePlayerCommand, ChangePlayerStyleCommand, AddActionCommand, RemoveActionCommand
from .figure_commands import MoveFigureCommand, ChangeFigureStyleCommand, ChangeFigureSizeCommand
from .label_commands import MoveLabelCommand, ChangeLabelTextAttributesCommand, ChangeLabelSizeCommand
from .action_commands import AddOptionalActionCommand

__all__ = ('PlaceFirstTeamCommand', 'PlaceSecondTeamCommand', 'RemoveSecondTeamCommand',
           'PlaceAdditionalPlayerCommand', 'RemoveAdditionalOffencePlayerCommand', 'RemoveAllPlayersCommand',
           'ChangeSecondTeamSymbolsCommand', 'RemoveAllActionsCommand', 'AddOptionalActionCommand',
           'PlaceFigureCommand', 'RemoveFigureCommand', 'RemoveAllFiguresCommand',
           'PlacePencilLinesCommand', 'RemovePencilLinesCommand',
           'PlaceLabelCommand', 'RemoveLabelCommand', 'RemoveAllLabelsCommand',
           'MoveFigureCommand', 'ChangeFigureStyleCommand', 'ChangeFigureSizeCommand',
           'MoveLabelCommand', 'ChangeLabelTextAttributesCommand', 'ChangeLabelSizeCommand',
           'MovePlayerCommand', 'ChangePlayerStyleCommand', 'AddActionCommand', 'RemoveActionCommand')