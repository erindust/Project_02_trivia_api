import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  7/26/23 done @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app,origins="*")  

  '''
  7/26/23 done @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add(
        "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
    )
    response.headers.add(
        "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
    )
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route("/categories")
  def retrieve_categories():
    selection = Category.query.order_by(Category.id).all()
    print(selection)
    
    if len(selection) == 0:
      abort(404)

    return jsonify(
      {
        "success": True,
        "categories": str(selection),
        "total_categories": len(Category.query.all())
      }
    )




  '''
  9/10/2023 DONE @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  def paginate_questions(request,selection):
    page = request.args.get("page",1,type=int)
    start = (page-1)*QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions

  @app.route("/questions")
  def retrieve_questions():
    selection = Question.query.order_by(Question.id).all()
    print(selection)
    current_questions = paginate_questions(request,selection)

    if len(current_questions) == 0:
      abort(404)

    return jsonify(
      {
        "success":True,
        "questions":current_questions ,
        "total_questions":len(Question.query.all())
      }
    )

  # Test endpoirt
  @app.route("/")
  def generic_endpoint():
    return jsonify(
        {
          "success":True,
        }
      )

  @app.route("/questions/<int:question_id>", methods=["GET"])
  def get_question(question_id):
    try:  
      question = Question.query.filter(Question.id==question_id).one_or_none()
      print(question)
      if question == None:
        abort(404)

      selection = Question.query.order_by(Question.id).all()
      print(selection)
      current_questions = paginate_questions(request,selection)
      # questions = [question.format() for question in selection]
      # print(questions)
      return jsonify(
        {

          "success":True,
          "questions":current_questions,
          "total_questions":len(selection)
        }
      )
    except:
      abort(422)


  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 

  8/12/2023 Need to figure out how to test this.
  9/12/2023 DONE
  '''
  @app.route("/questions/<int:question_id>", methods=["DELETE"])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id==question_id).one_or_none()
      print(question)
      if question == None:
        abort(404)

      question.delete()
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request,selection)

      return jsonify(
        {

          "success":True,
          "deleted":question_id,
          "questions":current_questions,
          "total_questions":len(Question.query.all()),
          "question":Question.query.filter(Question.id==question_id).one_or_none()
        }
      )
    except:
      abort(422)



  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route("/questions", methods=["POST"])
  def create_question():
    body = request.get_json()

    new_question = body.get("question",None)
    new_answer = body.get("answer",None)
    new_difficulty = body.get("difficulty",None)
    new_category = body.get("category",None)

    try:
      question = Question(question=new_question, answer=new_answer,difficulty=new_difficulty,catagory=new_category)
      question.insert()

      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request,selection)

      return jsonify(
        {
          "success":True,
          "created":question.id,
          "questions":current_questions,
          "total_questions":len(Question.query.all())
        }
      )
    except:
      abort(422)


  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route("/questions/search",methods=["POST"])
  def search_questions():
    body = request.get_json()
    searchPhrase = body.get("searchTerm",None)

    if searchPhrase == None:
      abort(404)

    searchResults = Question.query.filter(Question.question.ilike(str(searchPhrase))).all()

    return jsonify({
        'success': True,
        'questions': [question.format() for question in searchResults],
        'total_questions': len(searchResults),
        'current_category': None
    })



  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route("/categories/<int:category_id>/questions",methods=["GET"])
  def getQuestionsPerCategory(category_id):

    questions = Question.query.filter(Question.catagory == str(category_id)).all()

    if questions == None:
      abort(404)

    return jsonify({
      "success":True,
      "questions":[question.format() for question in questions],
      "total_questions":len(questions),
      "current_category":category_id
    })


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  # @app.route("/category/<int:category_id>/questions",methods=["POST"])
  # def play(category_id):
  #   questions = Question.query.filter(Questions.category == str(category_id)).all()
  #   if questions == None:
  #     abort(404)

  #   return jsonify({
  #     "success":True,
  #     "questions":[question.format() for question in questions],
  #     "total_questions":len(questions),
  #     "current_category":category_id
  #   })

  @app.route("/quizzes", methods=["POST"])
  def getTriviaQuestions():
    data = request.get_json()

    if data == None:
      abort(404)

    previous_questions = data["previous_questions"]
    category_id = data["quiz_catagory"]

    questions = Question.query.filter(Question.catagory == str(category_id)).all()
    questions_not_used = []
    for i in questions:
      # get all of the questions not used
      if i.id in previous_questions == False:
        questions_not_used.append(i.id)

    picked_question_index = random.randint(0,len(questions_not_used))


    return jsonify({
      "success": True,
      "id":questions_not_used(picked_question_index)
    })



    return jsonify({
      "id":question_id,
      "question":question,
      "answer":answer,
      "difficult":difficulty,
      "category":category_id

    })

    

    


  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return (
      jsonify({"success":False, "error":404, "message":"resource not found"}),
      404
    )

  @app.errorhandler(422)
  def unprocessable(error):
    return (
        jsonify({"success": False, "error": 422, "message": "unprocessable"}),
        422,
    )

  @app.errorhandler(400)
  def bad_request(error):
    return (
      jsonify({"success": False, "error": 400, "message": "bad request"}), 
      400
    )

  
  return app

    