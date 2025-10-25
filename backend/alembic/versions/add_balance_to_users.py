"""Add balance field to users table

Revision ID: add_balance_to_users
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_balance_to_users'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Agregar campo balance a la tabla users
    op.add_column('users', sa.Column('balance', sa.Float(), nullable=True, default=0.0))


def downgrade():
    # Remover campo balance de la tabla users
    op.drop_column('users', 'balance')




















