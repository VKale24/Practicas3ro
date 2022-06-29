"""Create, delete and update records with SQLAlchemy's ORM."""
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from source.models.CompanyModelDB import CompanyBase


def orm_create_company(session: Session, company: CompanyBase) -> CompanyBase:
    """
    Create a new instance of our `User` model.

    :param session: SQLAlchemy database session.
    :type session: Session
    :param user: User data model for creation.
    :type user: User

    :return: User
    """
    try:
        session.add(company)  # Add the user
        session.commit()  # Commit the change
        return company
    except IntegrityError as e:
        raise e.orig
    except SQLAlchemyError as e:
        raise e