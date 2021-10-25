from .. import db

class RubyChallenge(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(256)) #Path to source file
    tests_code = db.Column(db.String(256)) #Path to test suite file
    repair_objective = db.Column(db.String(128))
    complexity = db.Column(db.String(3))
    best_score = db.Column(db.Integer())

    def get_dict(self):
        return {
            "id":self.id,
            "code":self.code,
            "tests_code":self.tests_code,
            "repair_objective":self.repair_objective,
            "complexity":self.complexity,
            "best_score":self.best_score
        }

    @staticmethod
    def get_challenge(id):
        return db.session.query(RubyChallenge).filter_by(id=id).first()

    @staticmethod
    def get_challenges():
        return db.session.query(RubyChallenge).all()

    @staticmethod
    def get_all_challenges_dict():
        return list(map(lambda x: x.get_dict(), RubyChallenge.get_challenges()))

    @staticmethod
    def create_challenge(code, tests_code, repair_objective, complexity):
        challenge = RubyChallenge(
            code = code,
            tests_code = tests_code,
            repair_objective = repair_objective,
            complexity = complexity,
            best_score = 0
        )
        db.session.add(challenge)
        db.session.commit()
        return challenge.get_dict()

    @staticmethod
    def update_challenge(id, changes):
        if len(changes) == 0:
            return 1
        result = db.session.query(RubyChallenge).filter_by(id=id).update(changes)
        db.session.commit()
        return result

    @staticmethod
    def exists(id):
        return RubyChallenge.get_challenge(id) is not None