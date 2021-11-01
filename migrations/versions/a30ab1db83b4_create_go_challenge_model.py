"""create_go_challenge_model

Revision ID: a30ab1db83b4
Revises: 5d1b887ff54f
Create Date: 2021-10-11 19:43:43.891781

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a30ab1db83b4'
down_revision = '5d1b887ff54f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('go_challenge',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=256), nullable=True),
    sa.Column('tests_code', sa.String(length=256), nullable=True),
    sa.Column('repair_objective', sa.String(length=128), nullable=True),
    sa.Column('complexity', sa.String(length=3), nullable=True),
    sa.Column('best_score', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('go_challenge')
    # ### end Alembic commands ###
