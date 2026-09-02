"""Add restaurant and menu items

Revision ID: f02033cddcf7
Revises:
Create Date: 2026-08-25 13:54:51.170759
"""

from alembic import op
import sqlalchemy as sa


revision = "f02033cddcf7"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "restaurant",
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False
        ),
        sa.Column(
            "name",
            sa.String(length=100),
            nullable=False
        ),
        sa.Column(
            "cuisine_type",
            sa.String(length=50),
            nullable=False
        ),
        sa.Column(
            "default_menu_language",
            sa.String(length=20),
            nullable=False
        ),
        sa.PrimaryKeyConstraint("id")
    )

    op.create_table(
        "menu_item",
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False
        ),
        sa.Column(
            "restaurant_id",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "name",
            sa.String(length=100),
            nullable=False
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=False
        ),
        sa.Column(
            "detected_source_language",
            sa.String(length=20),
            nullable=False
        ),
        sa.Column(
            "price",
            sa.Numeric(precision=10, scale=2),
            nullable=False
        ),
        sa.Column(
            "category",
            sa.String(length=50),
            nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["restaurant_id"],
            ["restaurant.id"]
        ),
        sa.PrimaryKeyConstraint("id")
    )


def downgrade():
    op.drop_table("menu_item")
    op.drop_table("restaurant")