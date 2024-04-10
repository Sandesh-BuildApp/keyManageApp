from flask import Flask, render_template, url_for, redirect, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, current_user, login_required, logout_user
from flask_bcrypt import Bcrypt
import re


app = Flask(__name__,template_folder='templates')
login_manager = LoginManager(app)
bcrypt = Bcrypt(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'dfgtesa345Oljyfu0O'
# app.config['SESSION_COOKIE_SECURE'] = True  # Ensure cookies are only sent over HTTPS
# app.config['SESSION_COOKIE_HTTPONLY'] = True  # Mitigate XSS attacks by preventing access to cookies via JavaScript
# app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Protect against CSRF attacks by setting SameSite attribute

db = SQLAlchemy(app)



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    # is_active = db.Column(db.Boolean(), default=True)

    def __repr__(self):
        return f'<User {self.username}>'


@login_manager.user_loader
def load_user(user_id):
    user = db.session.get(User, int(user_id))
    if user:
        return user
    else:
        return None  # Or handle the missing user case differently


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
       
        login_id = request.form['login_id']  # This can be either username or email
        password = request.form['password']
        user = User.query.filter((User.username == login_id) | (User.email == login_id)).first()

        if user:
            if bcrypt.check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('keyManage'))
            else:
                flash('Invalid password', 'error')
        else:
            flash('Username not found. Please register.', 'error')
            # return redirect(url_for('register'))

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
    
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # # Validate email address
        # if not re.match(r'^[a-zA-Z0-9._%+-]+@nohara-inc\.co\.jp$', email):
        #     flash('Please use a valid email address ending with @nohara-inc.co.jp', 'error')
        #     return redirect(url_for('register'))
        
        # Validate email address both
        if not re.match(r'^[a-zA-Z0-9._%+-]+@(nohara-inc\.co\.jp|gmail\.com)$', email):
            flash('Please use a valid email address ending with @nohara-inc.co.jp or @gmail.com', 'error')
            return redirect(url_for('register'))

    
        # Check if the username or email already exists in the database
        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        if existing_user:
            flash('Username already exists. Please choose a different one.', 'error')
        elif existing_email:
            flash('Email already exists. Please use a different email.', 'error')
        else:
            # Hash the password
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            # Create a new user
            new_user = User(username=username, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()

            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))


    return render_template('registeration.html')



@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        
        # Check if the email exists in the database
        user = User.query.filter_by(email=email).first()

        if user:
            # Delete the user account from the database
            db.session.delete(user)
            db.session.commit()

            flash('Your account has been deleted. Please register again.', 'success')
            return redirect(url_for('register'))
        else:
            flash('Email not found. Please enter a valid email.', 'error')

    return render_template('forgot_password.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


## deploy AI app logic from here

# key management app
import ast
import os
from threading import Timer
from keyManageUtils import read_file, draw_graph_floorwise, modify_colors

# Define a custom sorting key function to extract the numerical part
def custom_sort_key(item):
    if item[:-2].isdigit():
        return int(item[:-2])
    else:
        return float('inf')  # Place non-numeric entries at the end

class DatastoreKey():
    df = None
    graph_lists = None
    nodes_list = None
    filename = None
    name = None
    visualization_type = None
    node_info = None
    node_list = None, 
    edge_from=None, 
    edge_to=None

datastoreKey = DatastoreKey()



@app.route('/keyManage')
@login_required
def keyManage():

    # print("User ID:", current_user.id)
    # print("Username:", current_user.username)
    # print("Email:", current_user.email)
    return render_template('keyManage.html')

@app.route('/keyManage', methods=['GET', 'POST'])
@login_required
def visualize():
    # if request.method == 'POST':
    if 'file' in request.files:
        f = request.files['file']

        file_str = f.filename.split(".")
        f.filename = f"datafile.{file_str[-1]}"
        f.save(os.path.join(app.static_folder,f.filename))
        datafile = os.path.join(app.static_folder,f.filename)

        df = read_file(datafile)
        # df.to_excel('static\datafile1.xlsx')
        graph_lists = df['部屋から: レベル'].unique()
        # Sort the list using the custom sorting key function
        sorted_room_level = sorted(graph_lists, key=custom_sort_key)


        datastoreKey.df = df
        datastoreKey.graph_lists = sorted_room_level
        datastoreKey.name = file_str[0]

    return render_template('keyManage.html', file_names=sorted_room_level)

@app.route('/visualize', methods=['POST'])
@login_required
def adjust_positions():
    
    name = request.form['graph_select']
    visualization_type = request.form.get('visualization')

    if name:
        html_text_utf8, node_list, edge_from, edge_to, node_info = draw_graph_floorwise(datastoreKey.df, name, visualization_type)

        # Generate unique filename
        # timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        # random_token = ''.join(random.choices(string.ascii_lowercase, k=10))
        # filename = f"部屋の接続グラフ_{name}_{timestamp}_{random_token}.html"
        # filename = f"部屋の接続グラフ_{name}.html"
        filename = f"{datastoreKey.name}_{name}.html"
        new_filename = os.path.join('static', filename)

        # # Check if file already exists and remove it before creating a new one
        # if os.path.exists(new_filename):
        #     os.remove(new_filename)

        # Write the encoded HTML text to a file
        with open(new_filename, 'wb') as file_handle:
            file_handle.write(html_text_utf8)

        # Read the selected file
        # selected_file = './static/graph.html'
        with open(new_filename, 'r', encoding='utf-8') as file:
            html_content = file.read()

        # Schedule deletion of the temporary file after 1 minute
        Timer(600, lambda: os.remove(new_filename)).start()

        # node_list = ['1', '2', '4']
        datastoreKey.filename = new_filename
        # datastore.name = name
        datastoreKey.visualization_type = visualization_type
        datastoreKey.node_info = node_info
        datastoreKey.node_list = node_list
        datastoreKey.edge_from = edge_from
        datastoreKey.edge_to = edge_to

        # print(node_list)


        # Pass file content and selected file to the template
        return render_template('keyManage.html', file_names=datastoreKey.graph_lists, html_content=html_content, selected_file=new_filename,node_list=node_list, edges=(edge_from, edge_to))
    else:
        return render_template('keyManage.html', file_names=datastoreKey.graph_lists, html_content=html_content, selected_file=None, node_list=None, edges=None)


@app.route('/color_nodes', methods=['POST'])
@login_required
def color_nodes():
    
    node_color_combinations = request.form.getlist('node_color_combinations[]')

    if node_color_combinations:
        # Convert strings to lists
        node_color_combinations = [ast.literal_eval(item) for item in node_color_combinations]

    node_info, html_text_utf8 = modify_colors(datastoreKey.node_info, node_color_combinations, None, datastoreKey.visualization_type)
    datastoreKey.node_info = node_info
    new_filename = datastoreKey.filename
    # Write the encoded HTML text to a file
    with open(new_filename, 'wb') as file_handle:
        file_handle.write(html_text_utf8)

    with open(new_filename, 'r', encoding='utf-8') as file:
        html_content = file.read()


    return render_template('keyManage.html', file_names=datastoreKey.graph_lists, html_content=html_content, selected_file=new_filename, node_list=datastoreKey.node_list, edges=(datastoreKey.edge_from, datastoreKey.edge_to))


@app.route('/color_edges', methods=['POST'])
@login_required
def color_edges():
    
    edge_color_combinations = request.form.getlist('edge_combinations[]')

    if edge_color_combinations:
        edge_color_combinations = [ast.literal_eval(item) for item in edge_color_combinations]

    node_info, html_text_utf8 = modify_colors(datastoreKey.node_info, None, edge_color_combinations, datastoreKey.visualization_type)
    datastoreKey.node_info = node_info
    new_filename = datastoreKey.filename
    # Write the encoded HTML text to a file
    with open(new_filename, 'wb') as file_handle:
        file_handle.write(html_text_utf8)

    with open(new_filename, 'r', encoding='utf-8') as file:
        html_content = file.read()

    return render_template('keyManage.html', file_names=datastoreKey.graph_lists, html_content=html_content, selected_file=new_filename, node_list=datastoreKey.node_list, edges=(datastoreKey.edge_from, datastoreKey.edge_to))




@app.route('/pointCloud')
@login_required
def pointCloud():
    return render_template('pointCloud.html')

@app.route('/floorGAN')
@login_required
def floorGAN():

    return render_template('floorGAN.html')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    # app.run(debug=True)
    # app.run(host='127.0.0.1', port=8080, debug=True)
    app.run(host='0.0.0.0', port=8080, debug=True)
