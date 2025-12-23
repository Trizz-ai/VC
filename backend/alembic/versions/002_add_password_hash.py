"""Add password hash to contacts

Revision ID: 002
Revises: 001
Create Date: 2025-10-25 08:20:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add password_hash column to contacts table
    op.add_column('contacts', sa.Column('password_hash', sa.String(255), nullable=True))


def downgrade() -> None:
    # Remove password_hash column from contacts table
    op.drop_column('contacts', 'password_hash')
