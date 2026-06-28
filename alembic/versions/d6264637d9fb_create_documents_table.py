"""create documents table

Revision ID: d6264637d9fb
Revises: 
Create Date: 2026-06-28 01:39:28.221787

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd6264637d9fb'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension — must exist before the Vector column type can be used
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True,
                  comment="Unique ID for this specific chunk row"),
        sa.Column("source_document_id", sa.String(36), nullable=False, index=True,
                  comment="UUID grouping all chunks of one uploaded document"),
        sa.Column("title", sa.String(500), nullable=False,
                  comment="Title of the original document"),
        sa.Column("source", sa.String(200), nullable=True, index=True,
                  comment="Where this document came from: e.g. 'support_docs', 'faq', 'manual'"),
        sa.Column("chunk_index", sa.Integer(), nullable=False,
                  comment="Position of this chunk within the original document (0-based)"),
        sa.Column("chunk_total", sa.Integer(), nullable=False,
                  comment="Total number of chunks the original document was split into"),
        sa.Column("content", sa.Text(), nullable=False,
                  comment="The actual text content of this chunk"),
        # Vector(1536) cannot be expressed via SQLAlchemy types in Alembic autogenerate,
        # so we add the column with raw SQL after the table is created.
        sa.Column("embedding", sa.Text(), nullable=True),  # placeholder, replaced below
        sa.Column("created_at", sa.DateTime(), nullable=False,
                  server_default=sa.func.now()),
    )

    # Replace the placeholder Text column with the real vector(1536) type
    op.execute("ALTER TABLE documents ALTER COLUMN embedding TYPE vector(1536) USING NULL")


def downgrade() -> None:
    op.drop_table("documents")
    op.execute("DROP EXTENSION IF EXISTS vector")
