"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create contacts table
    op.create_table('contacts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('ghl_contact_id', sa.String(length=100), nullable=True),
        sa.Column('consent_granted', sa.Boolean(), nullable=False),
        sa.Column('consent_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contacts_email'), 'contacts', ['email'], unique=True)
    op.create_index(op.f('ix_contacts_ghl_contact_id'), 'contacts', ['ghl_contact_id'], unique=True)
    op.create_index(op.f('ix_contacts_phone'), 'contacts', ['phone'], unique=False)

    # Create meetings table
    op.create_table('meetings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('address', sa.String(length=500), nullable=False),
        sa.Column('lat', sa.Float(), nullable=False),
        sa.Column('lng', sa.Float(), nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('qr_code', sa.String(length=100), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_meetings_is_active'), 'meetings', ['is_active'], unique=False)
    op.create_index(op.f('ix_meetings_name'), 'meetings', ['name'], unique=False)
    op.create_index(op.f('ix_meetings_qr_code'), 'meetings', ['qr_code'], unique=True)

    # Create sessions table
    op.create_table('sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('contact_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('meeting_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('dest_name', sa.String(length=255), nullable=False),
        sa.Column('dest_address', sa.String(length=500), nullable=False),
        sa.Column('dest_lat', sa.Float(), nullable=False),
        sa.Column('dest_lng', sa.Float(), nullable=False),
        sa.Column('session_notes', sa.Text(), nullable=True),
        sa.Column('is_complete', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ),
        sa.ForeignKeyConstraint(['meeting_id'], ['meetings.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sessions_contact_id'), 'sessions', ['contact_id'], unique=False)
    op.create_index(op.f('ix_sessions_is_complete'), 'sessions', ['is_complete'], unique=False)
    op.create_index(op.f('ix_sessions_meeting_id'), 'sessions', ['meeting_id'], unique=False)

    # Create session_events table
    op.create_table('session_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.Enum('check_in', 'check_out', name='eventtype'), nullable=False),
        sa.Column('ts_client', sa.DateTime(timezone=True), nullable=False),
        sa.Column('ts_server', sa.DateTime(timezone=True), nullable=False),
        sa.Column('lat', sa.Float(), nullable=False),
        sa.Column('lng', sa.Float(), nullable=False),
        sa.Column('location_flag', sa.Enum('granted', 'denied', 'timeout', name='locationflag'), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_session_events_session_id'), 'session_events', ['session_id'], unique=False)
    op.create_index(op.f('ix_session_events_type'), 'session_events', ['type'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_session_events_type'), table_name='session_events')
    op.drop_index(op.f('ix_session_events_session_id'), table_name='session_events')
    op.drop_table('session_events')
    op.drop_index(op.f('ix_sessions_meeting_id'), table_name='sessions')
    op.drop_index(op.f('ix_sessions_is_complete'), table_name='sessions')
    op.drop_index(op.f('ix_sessions_contact_id'), table_name='sessions')
    op.drop_table('sessions')
    op.drop_index(op.f('ix_meetings_qr_code'), table_name='meetings')
    op.drop_index(op.f('ix_meetings_name'), table_name='meetings')
    op.drop_index(op.f('ix_meetings_is_active'), table_name='meetings')
    op.drop_table('meetings')
    op.drop_index(op.f('ix_contacts_phone'), table_name='contacts')
    op.drop_index(op.f('ix_contacts_ghl_contact_id'), table_name='contacts')
    op.drop_index(op.f('ix_contacts_email'), table_name='contacts')
    op.drop_table('contacts')
