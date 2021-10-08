"""create model JavaScriptChallenge

Revision ID: 5d1b887ff54f
Revises: 47a356299a25
Create Date: 2021-10-08 18:41:26.041040

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5d1b887ff54f'
down_revision = '47a356299a25'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('challenge_java',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=128), nullable=False),
    sa.Column('tests_code', sa.String(length=128), nullable=False),
    sa.Column('repair_objective', sa.String(length=128), nullable=False),
    sa.Column('complexity', sa.Integer(), nullable=False),
    sa.Column('score', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('challenge_java')
    # ### end Alembic commands ###
