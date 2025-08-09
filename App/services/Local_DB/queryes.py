import os
from sqlalchemy import text

from Config import DB_URL
from services.Local_DB import engine
from services.Local_DB import Base, session_factory
from .mappers import PlaybookMapperLocalDB


# if TYPE_CHECKING:
from .models import PlaybookORM


def drop_tables() -> None:
    Base.metadata.drop_all(engine)  # для отладки


def check_db_is_created() -> bool:
    return os.path.exists(DB_URL)


def create_db_if_not_exists() -> None:
    if not check_db_is_created():
        Base.metadata.create_all(engine)



def save_playbook(playbook: 'PlaybookWidget', is_new_playbook: bool) -> 'PlaybookORM':
    with session_factory() as session:
        mapper = PlaybookMapperLocalDB(is_new_playbook)
        playbook_orm = mapper.get_valid_playbook_orm(playbook)
        session.add(playbook_orm)
        session.commit()

        # print(f'{playbook_orm = }')
        mapper.update_app_obj_ids_from_db(playbook_orm)
        return playbook_orm



def get_playbook_by_id(obj_id: int) -> 'PlaybookORM':
    with session_factory() as session:
        playbook_orm = session.get(PlaybookORM, obj_id)
        return playbook_orm






# def select_playbook(playbook_id: int) -> 'PlaybookORM':
#     with session_factory() as session:
#         statement = (
#             select(PlaybookORM).where(PlaybookORM.playbook_id_pk == playbook_id)
#             .options(selectinload(PlaybookORM.schemes)
#                      .options(selectinload(SchemeORM.ellipses), selectinload(SchemeORM.rectangles),
#                               selectinload(SchemeORM.labels), selectinload(SchemeORM.pencil_lines),
#                               selectinload(SchemeORM.players)
#                               .options(selectinload(PlayerORM.lines),
#                                        selectinload(PlayerORM.action_finishes_arr),
#                                        selectinload(PlayerORM.action_finishes_line)
#                                        )
#                               )
#                      )
#         )
#         res = session.execute(statement)
#         playbook = res.unique().scalars().all()[0]
#         return playbook


def get_playbook_info() -> list[tuple]:
    with session_factory() as session:
        query = text('SELECT id, playbook_name, playbook_type, updated_at, created_at FROM playbooks')
        res = session.execute(query)
        return res.all()


# def get_playbook_names() -> list[str]:
#     with session_factory() as session:
#         query = text('SELECT playbook_name FROM playbooks')
#         res = session.execute(query)
#         return res.scalars().all()


# def delete_playbook(playbook_id: int) -> None:
#     with session_factory() as session:
#         statement = (
#             select(PlaybookORM).where(PlaybookORM.playbook_id_pk == playbook_id)
#             .options(selectinload(PlaybookORM.schemes)
#                      .options(selectinload(SchemeORM.ellipses), selectinload(SchemeORM.rectangles),
#                               selectinload(SchemeORM.labels), selectinload(SchemeORM.pencil_lines),
#                               selectinload(SchemeORM.players)
#                               .options(selectinload(PlayerORM.lines),
#                                        selectinload(PlayerORM.action_finishes_arr),
#                                        selectinload(PlayerORM.action_finishes_line)
#                                        )
#                               )
#                      )
#         )
#         res = session.execute(statement)
#         playbook = res.unique().scalars().all()[0]
#         session.delete(playbook)
#         session.commit()
