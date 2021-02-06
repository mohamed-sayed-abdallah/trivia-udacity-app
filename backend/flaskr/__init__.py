import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from random import randint
from models import setup_db, Question, Category,db



def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  #CORS(app,resources={r"*/api/*": {"origins":"*"}})
  CORS(app)
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
    return response
  '''
  
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  
  @app.route('/categories')
  def get_all_categories():
    all_categories=Category.query.all()
    list_allcategories=[]
    categ_id=[]
    categ_obj=[]
    formated_categories=[category.format() for category in all_categories]
    for category in all_categories:
        list_allcategories.append(category.type)
        categ_id.append(category.id)
    categ_obj=dict(zip(categ_id,list_allcategories))
    return jsonify({
      'success':True,
      'categories':categ_obj
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  def paginate_questions(request,collection):
    page=request.args.get('page',1,type=int)
    start=(page-1)*10
    end=start+10
    return collection[start:end]
  @app.route('/questions')
  def get_all_questions():  
    all_questions=Question.query.all()
    all_categories=Category.query.all()
    proposed=[]
    list_allcategories=[]
    categ_id=[]
    categ_obj=[]
    for category in all_categories:
        list_allcategories.append(category.type)
        categ_id.append(category.id)
    categ_obj=dict(zip(categ_id,list_allcategories))
    for question in all_questions:
      proposed.append(question.format())
    all_quest=proposed      
    proposed=paginate_questions(request,proposed)
    if(len(proposed)==0):
      abort(404)
    return jsonify({
      'success':True,
       'questions':proposed,
       'total_questions':len(all_quest),
       'current_category':None,
       'categories':categ_obj 
    })
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>',methods=["DELETE"])
  def delete_question(question_id):
    try:
      deleted_item=Question.query.get(question_id)
      Question.delete(deleted_item)
      if(deleted_item is None):
        abort(404)
      all_questions=Question.query.all()
      return jsonify({
       'success':True,
       'deleted':question_id
      })
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
  @app.route('/questions',methods=["POST"])
  def create_question():
    body=request.get_json()
    proposed=[]
    po_question=body.get('question')
    po_answer=body.get('answer')
    po_category=body.get('category')
    po_difficulty=body.get('difficulty')
    if not (po_question and po_answer and po_category and po_difficulty):
      abort(400)
    try:
     inserted_item=Question(
       question=po_question,
       answer=po_answer,
       category=po_category,
       difficulty=po_difficulty
      )
     question=Question.insert(inserted_item)
     all_questions=Question.query.all()
     for question in all_questions:
       proposed.append(question.format())     
     proposed=paginate_questions(request,proposed)
     return jsonify({
       'success':True,
       'created':question.id,
       'questions': proposed,
       'total_questions': len(all_questions)
     })
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
  @app.route('/questions/search',methods=["POST"])
  def search_question():
    body=request.get_json()
    search_term=body.get('searchTerm')
    search_results=[]
    if not (search_term):
      abort(400)
    try:
      selected_items=Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
      for selected_question in selected_items:
        search_results.append({
          'question_id':selected_question.id,
          'questions':selected_question.question,
          'currentCategory':selected_question.category
        })
      return jsonify({
        'success':True,
        'question_id':[search_results[index].get('question_id') for index in range(len(search_results))],
        'questions':[question.format() for question in selected_items],
        'currentCategory':[search_results[index].get('currentCategory') for index in range(len(search_results))],
        'totalQuestions':len(search_results)
      })
    except:
      abort(422)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:categoryid>/questions')
  def get_questions_by_categories(categoryid):
    try:
      list_allcategories=[]
      categ_id=[]
      categ_obj=[]
      all_categories=Category.query.all()
      for category in all_categories:
        list_allcategories.append(category.type)
        categ_id.append(category.id)
      categ_obj=dict(zip(categ_id,list_allcategories))

      questions_by_category=[]
      categories_list=set()
      cate=Category.query.filter(Category.id==categoryid).one_or_none()
      if(cate is None):
        abort(404)
      category_rows=Category.query.all()
      for category_row in category_rows:
        categories_list.add((category_row.id,category_row.type))
      for category_item in categories_list:
        questions_by_category.append({
          'category_id':category_item[0],
          'category':category_item[1],
          'questions':[]
        })
      question_rows=Question.query.all()
      for question_row in question_rows:
        question_items=db.session.query(Question).filter(question_row.id==Question.id).filter(question_row.question==Question.question).all()
        for question_item in question_items:
          for each_category in questions_by_category:
            if(question_item.category==each_category['category_id']):
              each_category['questions'].append({
                'question':question_item.question,
                'id':question_item.id,
                'category':question_item.category,
                'answer':question_item.answer,
                'difficulty':question_item.difficulty
              })
      selected_categoriezed_questions=[]
      for items_in_questions_category in questions_by_category:
        if(categoryid==items_in_questions_category['category_id']):
          selected_categoriezed_questions=items_in_questions_category
      return jsonify({
        'success':True,
        "questions":selected_categoriezed_questions.get('questions'),
        "total_questions":len(selected_categoriezed_questions.get('questions')),
        "current_category":selected_categoriezed_questions.get('category'),
        "categories":categ_obj
      })
    except:
      abort(422)
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
  @app.route('/quizzes',methods=["POST"])
  def play_quiz():
   body=request.get_json()
   previous_questions=body.get('previous_questions')
   quiz_category=body.get('quiz_category')
   current_question=[]
   if not (quiz_category):
     abort(400)
   try:
    ############## if all questions choosed ########################
    if(quiz_category['id']==0):
      questions_per_category=Question.query.all()
      questions_id_list=[]
      current_q_list=[]
      current_q_category=[]
      for quest_item in questions_per_category:
        questions_id_list.append(quest_item.id)
        q_id=quest_item.id
        if not (int(q_id) in previous_questions):
         current_q_list.append(q_id)
         current_q_category.append(quest_item)
    
        if(len(current_q_category)>0):
          for each_question in current_q_category:
            selected_id=random.choice(current_q_list)
            current_question=Question.query.get(int(selected_id)).format()    
        else:
          return jsonify({})
    else:
    ############## if certain category choosed ########################
     questions_per_category=Question.query.filter(Question.category==quiz_category['id']).all()
     questions_id_list=[]
     current_q_list=[]
     current_q_category=[]
     for quest_item in questions_per_category:
      questions_id_list.append(quest_item.id)
      q_id=quest_item.id
      if not (int(q_id) in previous_questions):
        current_q_list.append(q_id)
        current_q_category.append(quest_item)
    
      if(len(current_q_category)>0):
        for each_question in current_q_category:
          selected_id=random.choice(current_q_list)
          current_question=Question.query.get(int(selected_id)).format()
      else:
        return jsonify({})
          
    return jsonify({
        'success':True,
        'question':current_question
      })
   except:
     abort(422)

   
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error':404,
      'message': "resource not found"
    }),404
  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success': False,
      'error':422,
      'message': "unprocessed"
    }),422
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error':400,
      'message': "bad request"
    }),400
  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      'success': False,
      'error':405,
      'message': "This method is not allowed"
    }),405
  

  
  return app

    