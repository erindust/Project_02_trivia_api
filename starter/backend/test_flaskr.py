import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        # self.database_path = "postgres://{}/{}".format('postgres','postgres','localhost:5432', self.database_name)
        self.database_path = "postgresql://{}:{}@{}/{}".format("postgres", "postgres",'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_generic(self):
        res = self.client().get("/")
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)

    def test_access_get_a_record(self):
        question_id = 2
        res = self.client().get("/"+ str(question_id))
        data = json.loads(res.data)
        question = Question.query.filter(Question.id == question_id).one_or_none() 

    def test_delete_question(self):
        question_id = 2
        res = self.client().delete("/questions/"+str(question_id))
        data = json.loads(res.data).decode('utf-8')
        print(data)

        question = Question.query.filter(Question.id == question_id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['deleted'],question_id)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data[len(data['questions'])])
        self.assertEqual(question,None)

    def test_retrieve_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()