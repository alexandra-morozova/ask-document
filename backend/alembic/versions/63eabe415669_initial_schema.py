"""initial schema

Revision ID: 63eabe415669
Revises:
Create Date: 2026-10-10 19:49:06.653413

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision: str = "63eabe415669"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

MANAGED_TABLES = (
    "users",
    "chat_threads",
    "chat_messages",
    "message_citations",
    "source_documents",
    "document_chunks",
)


def upgrade() -> None:
    op.execute(sa.text("CREATE EXTENSION IF NOT EXISTS vector"))

    op.create_table(
        "source_documents",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("ticker", sa.Text(), nullable=False),
        sa.Column("company", sa.Text(), nullable=False),
        sa.Column("filing_type", sa.Text(), nullable=False),
        sa.Column("filing_date", sa.Date(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("accession_number", sa.Text(), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("markdown", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("accession_number"),
    )
    op.create_index("ix_source_documents_ticker", "source_documents", ["ticker"])

    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_foreign_key(
        "users_id_auth_users_fkey",
        "users",
        "users",
        ["id"],
        ["id"],
        referent_schema="auth",
        ondelete="CASCADE",
    )

    op.create_table(
        "chat_threads",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("owner_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chat_threads_owner_id", "chat_threads", ["owner_id"])

    op.create_table(
        "document_chunks",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("document_id", sa.UUID(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("page", sa.Integer(), nullable=True),
        sa.Column("section", sa.Text(), nullable=True),
        sa.Column("start_offset", sa.Integer(), nullable=True),
        sa.Column("end_offset", sa.Integer(), nullable=True),
        sa.Column("embedding", Vector(dim=1536), nullable=True),
        sa.Column(
            "search_vector",
            postgresql.TSVECTOR(),
            sa.Computed("to_tsvector('english', coalesce(text, ''))", persisted=True),
            nullable=False,
        ),
        sa.Column("token_count", sa.Integer(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["document_id"], ["source_documents.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("document_id", "chunk_index"),
    )
    op.create_index(
        "ix_document_chunks_document_id", "document_chunks", ["document_id"]
    )
    op.create_index(
        "document_chunks_embedding_hnsw",
        "document_chunks",
        ["embedding"],
        postgresql_using="hnsw",
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )
    op.create_index(
        "document_chunks_search_vector_gin",
        "document_chunks",
        ["search_vector"],
        postgresql_using="gin",
    )
    op.create_index(
        "document_chunks_metadata_gin",
        "document_chunks",
        ["metadata"],
        postgresql_using="gin",
    )

    op.create_table(
        "chat_messages",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("thread_id", sa.UUID(), nullable=False),
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["thread_id"], ["chat_threads.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("thread_id", "position"),
    )
    op.create_index("ix_chat_messages_thread_id", "chat_messages", ["thread_id"])

    op.create_table(
        "message_citations",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("message_id", sa.UUID(), nullable=False),
        sa.Column("chunk_id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["chunk_id"], ["document_chunks.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["message_id"], ["chat_messages.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("message_id", "chunk_id"),
    )
    op.create_index(
        "ix_message_citations_chunk_id", "message_citations", ["chunk_id"]
    )
    op.create_index(
        "ix_message_citations_message_id", "message_citations", ["message_id"]
    )

    op.execute(
        sa.text(
            """
            GRANT SELECT, INSERT, UPDATE, DELETE
            ON TABLE users, chat_threads, chat_messages, message_citations
            TO authenticated
            """
        )
    )
    op.execute(
        sa.text(
            """
            GRANT SELECT
            ON TABLE source_documents, document_chunks
            TO authenticated
            """
        )
    )
    op.execute(
        sa.text(
            """
            GRANT ALL
            ON TABLE users, chat_threads, chat_messages, message_citations,
                     source_documents, document_chunks
            TO service_role
            """
        )
    )

    for table in MANAGED_TABLES:
        op.execute(sa.text(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY"))

    op.execute(
        sa.text(
            """
            CREATE POLICY users_own_row ON users
            FOR ALL TO authenticated
            USING (id = (SELECT auth.uid()))
            WITH CHECK (id = (SELECT auth.uid()))
            """
        )
    )
    op.execute(
        sa.text(
            """
            CREATE POLICY chat_threads_owner ON chat_threads
            FOR ALL TO authenticated
            USING (owner_id = (SELECT auth.uid()))
            WITH CHECK (owner_id = (SELECT auth.uid()))
            """
        )
    )
    op.execute(
        sa.text(
            """
            CREATE POLICY chat_messages_owner ON chat_messages
            FOR ALL TO authenticated
            USING (
                EXISTS (
                    SELECT 1 FROM chat_threads
                    WHERE chat_threads.id = chat_messages.thread_id
                      AND chat_threads.owner_id = (SELECT auth.uid())
                )
            )
            WITH CHECK (
                EXISTS (
                    SELECT 1 FROM chat_threads
                    WHERE chat_threads.id = chat_messages.thread_id
                      AND chat_threads.owner_id = (SELECT auth.uid())
                )
            )
            """
        )
    )
    op.execute(
        sa.text(
            """
            CREATE POLICY message_citations_owner ON message_citations
            FOR ALL TO authenticated
            USING (
                EXISTS (
                    SELECT 1
                    FROM chat_messages
                    JOIN chat_threads ON chat_threads.id = chat_messages.thread_id
                    WHERE chat_messages.id = message_citations.message_id
                      AND chat_threads.owner_id = (SELECT auth.uid())
                )
            )
            WITH CHECK (
                EXISTS (
                    SELECT 1
                    FROM chat_messages
                    JOIN chat_threads ON chat_threads.id = chat_messages.thread_id
                    WHERE chat_messages.id = message_citations.message_id
                      AND chat_threads.owner_id = (SELECT auth.uid())
                )
            )
            """
        )
    )
    op.execute(
        sa.text(
            """
            CREATE POLICY source_documents_read ON source_documents
            FOR SELECT TO authenticated
            USING (true)
            """
        )
    )
    op.execute(
        sa.text(
            """
            CREATE POLICY document_chunks_read ON document_chunks
            FOR SELECT TO authenticated
            USING (true)
            """
        )
    )


def downgrade() -> None:
    op.drop_index("ix_message_citations_message_id", table_name="message_citations")
    op.drop_index("ix_message_citations_chunk_id", table_name="message_citations")
    op.drop_table("message_citations")
    op.drop_index("ix_chat_messages_thread_id", table_name="chat_messages")
    op.drop_table("chat_messages")
    op.drop_index("document_chunks_metadata_gin", table_name="document_chunks")
    op.drop_index("document_chunks_search_vector_gin", table_name="document_chunks")
    op.drop_index("document_chunks_embedding_hnsw", table_name="document_chunks")
    op.drop_index("ix_document_chunks_document_id", table_name="document_chunks")
    op.drop_table("document_chunks")
    op.drop_index("ix_chat_threads_owner_id", table_name="chat_threads")
    op.drop_table("chat_threads")
    op.drop_constraint("users_id_auth_users_fkey", "users", type_="foreignkey")
    op.drop_table("users")
    op.drop_index("ix_source_documents_ticker", table_name="source_documents")
    op.drop_table("source_documents")
