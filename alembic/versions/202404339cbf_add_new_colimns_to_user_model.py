"""Add new colimns to User model

Revision ID: 202404339cbf
Revises: 
Create Date: 2026-08-31 09:25:46.812136

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '202404339cbf'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('email', sa.String, nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    pass
