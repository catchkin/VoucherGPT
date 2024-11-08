"""initial schema

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2024-01-08 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect

# revision identifiers
revision = 'a1b2c3d4e5f6'
down_revision = None
branch_labels = None
depends_on = None


def check_enum_exists(conn, enum_name):
    """Check if enum exists using raw SQL"""
    query = """
    SELECT EXISTS (
        SELECT 1 
        FROM pg_type 
        WHERE typname = %s
    );
    """
    result = conn.execute(sa.text("SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = :name);"),
                          {'name': enum_name})
    return result.scalar()


def create_enum_if_not_exists(enum_name, enum_values):
    # Create connection
    conn = op.get_bind()

    # Check if enum exists
    if not check_enum_exists(conn, enum_name):
        # Create enum if it doesn't exist
        enum_values_str = "', '".join(enum_values)
        op.execute(f"CREATE TYPE {enum_name} AS ENUM ('{enum_values_str}')")


def drop_enum_if_exists(enum_name):
    conn = op.get_bind()
    if check_enum_exists(conn, enum_name):
        op.execute(f"DROP TYPE {enum_name}")


def upgrade() -> None:
    # Create enum types if they don't exist
    create_enum_if_not_exists(
        'documenttype',
        ['business_plan', 'company_profile', 'financial_report', 'training_data', 'other']
    )
    create_enum_if_not_exists(
        'sectiontype',
        ['executive_summary', 'company_overview', 'market_analysis', 'business_model',
         'financial_plan', 'technical_description', 'other']
    )

    # Create companies table
    op.create_table(
        'companies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('business_number', sa.String(length=20), nullable=True),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('establishment_date', sa.String(length=10), nullable=True),
        sa.Column('employee_count', sa.Integer(), nullable=True),
        sa.Column('annual_revenue', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_companies_business_number'), 'companies', ['business_number'], unique=True)
    op.create_index(op.f('ix_companies_name'), 'companies', ['name'], unique=False)

    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('type',
                  postgresql.ENUM('business_plan', 'company_profile', 'financial_report', 'training_data', 'other',
                                  name='documenttype', create_type=False), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('file_path', sa.String(length=512), nullable=True),
        sa.Column('file_name', sa.String(length=255), nullable=True),
        sa.Column('mime_type', sa.String(length=100), nullable=True),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create sections table
    op.create_table(
        'sections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('type', postgresql.ENUM('executive_summary', 'company_overview', 'market_analysis', 'business_model',
                                          'financial_plan', 'technical_description', 'other', name='sectiontype',
                                          create_type=False), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=True),
        sa.Column('meta_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('document_id', sa.Integer(), nullable=True),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Drop tables
    op.drop_table('sections')
    op.drop_table('documents')
    op.drop_table('companies')

    # Drop enum types if they exist
    drop_enum_if_exists('sectiontype')
    drop_enum_if_exists('documenttype')