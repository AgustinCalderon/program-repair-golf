"""Create RubyChallenge Model

Revision ID: 0cb84c718ecc
Revises: 8813889e1194
Create Date: 2021-10-07 20:44:49.320433

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0cb84c718ecc'
down_revision = '8813889e1194'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ruby_challenge',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=256), nullable=True),
    sa.Column('tests_code', sa.String(length=256), nullable=True),
    sa.Column('repair_objective', sa.String(length=128), nullable=True),
    sa.Column('complexity', sa.String(length=1), nullable=True),
    sa.Column('best_score', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.CheckConstraint("complexity IN ('1', '2', '3', '4', '5')")
    )
    op.create_table('ruby_attempts',
    sa.Column('challenge_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('count', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['challenge_id'], ['ruby_challenge.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ruby_challenge')
    op.drop_table('ruby_attempts')
    # ### end Alembic commands ###
