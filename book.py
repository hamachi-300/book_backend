from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from pymongo import MongoClient


# MongoDB connection
client = MongoClient('mongodb+srv://tuwaris:aUh1fCNMrFIMPfmd@tuwaris.5ynbx.mongodb.net/?retryWrites=true&w=majority&appName=Tuwaris')
db = client['books']
book_collection = db['book_infos']

# Flask app setup
app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Root route
@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# Read (GET) operation - Get all books
@app.route('/books', methods=['GET'])
@cross_origin()
def get_all_books():
    try:
        # Retrieve all books from the collection
        books_cursor = book_collection.find()
        
        # Convert the cursor to a list of dictionaries
        books_list = list(books_cursor)
        
        # Remove the MongoDB '_id' field (it's not JSON serializable)
        for book in books_list:
            book.pop('_id', None)
        # Return the list of books as a JSON response
        return jsonify(books_list)
    except Exception as e:
        # Handle any errors
        return jsonify({"error": str(e)})
    
# Read (GET) operation - Get a specific book by ID
@app.route('/books/<int:book_id>', methods=['GET'])
@cross_origin()
def get_book(book_id):
    try:
        # Query the book by its ID
        book = book_collection.find_one({"id": book_id})
        
        # If the book is not found, return a 404 error
        if not book:
            return jsonify({"error": "Book not found"}), 404
        
        # Convert the MongoDB '_id' field to a string
        book['_id'] = str(book['_id'])
        
        # Return the book as a JSON response
        return jsonify(book), 200
    except Exception as e:
        # Handle any errors
        return jsonify({"error": str(e)}), 500
    
# Update (PUT) operation
@app.route('/books/<int:book_id>', methods=['PUT'])
@cross_origin()
def update_book(book_id):
    try:
        # Get the JSON data from the request
        data = request.get_json()
        
        # Validate the input data
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Update the book in the MongoDB collection
        result = book_collection.update_one({"id": book_id}, {"$set": data})
        
        # Check if the book was found and updated
        if result.matched_count == 0:
            return jsonify({"error": "Book not found"}), 404
        
        # Fetch the updated book
        updated_book = book_collection.find_one({"id": book_id})
        updated_book['_id'] = str(updated_book['_id'])
        
        # Return the updated book as a JSON response
        return jsonify(updated_book), 200
    except Exception as e:
        # Handle any errors
        return jsonify({"error": str(e)}), 500

# Delete operation
@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    try:
        # Delete the book from the MongoDB collection
        result = book_collection.delete_one({"id": book_id})
        
        # Check if the book was found and deleted
        if result.deleted_count == 0:
            return jsonify({"error": "Book not found"}), 404
        
        # Return a success message
        return jsonify({"message": "Book deleted successfully"}), 200
    except Exception as e:
        # Handle any errors
        return jsonify({"error": str(e)}), 500

# Create (POST) operation
@app.route('/books', methods=['POST'])
@cross_origin()
def create_book():
    try:
        # Get the JSON data from the request
        data = request.get_json()

        # Validate the input data
        if not data or not all(key in data for key in ["title", "author", "image_url"]):
            return jsonify({"error": "Missing required fields"}), 400

        # Generate a new ID (if needed)
        # Note: If your MongoDB documents use `ObjectId`, you don't need to manually generate an ID.
        last_book = book_collection.find_one(sort=[("id", -1)])
        new_id = last_book["id"] + 1 if last_book else 1

        # Create a new book document
        new_book = {
            "id": new_id,  # Assign the new ID
            "title": data["title"],
            "author": data["author"],
            "image_url": data["image_url"]
        }

        # Insert the new book into the MongoDB collection
        result = book_collection.insert_one(new_book)

        # Add the MongoDB-generated `_id` to the response
        new_book["_id"] = str(result.inserted_id)

        # Return the new book as a JSON response with a 201 status code
        return jsonify(new_book), 201
    except Exception as e:
        # Handle any errors
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)