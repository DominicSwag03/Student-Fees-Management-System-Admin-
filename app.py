# app.py
from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Student, FeeType, Payment
from forms import LoginForm, RegistrationForm, FeeTypeForm, PaymentForm, StudentForm
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///student_fees.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables
@app.before_request
def create_tables():
    db.create_all()
    
    # Create admin user if not exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', email='admin@example.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

# Route for home page
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

# Route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

# Route for logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

# Route for dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    students_count = Student.query.count()
    payments_count = Payment.query.count()
    recent_payments = Payment.query.order_by(Payment.payment_date.desc()).limit(5).all()
    total_collected = db.session.query(db.func.sum(Payment.amount)).scalar() or 0
    
    return render_template('dashboard.html', 
                           students_count=students_count,
                           payments_count=payments_count,
                           recent_payments=recent_payments,
                           total_collected=total_collected)

# Registration routes
@app.route('/register_student', methods=['GET', 'POST'])
@login_required
def register_student():
    form = StudentForm()
    if form.validate_on_submit():
        # Generate a unique admission number
        last_student = Student.query.order_by(Student.id.desc()).first()
        admission_no = f"STU{datetime.now().year}{last_student.id + 1 if last_student else 1:04d}"
        
        # Create user for student
        user = User(username=form.email.data, email=form.email.data, role='student')
        user.set_password(form.phone_no.data)  # Use phone number as initial password
        db.session.add(user)
        db.session.flush()  # To get the user ID
        
        # Create student
        student = Student(
            admission_no=admission_no,
            name=form.name.data,
            date_of_birth=form.date_of_birth.data,
            phone_no=form.phone_no.data,
            email=form.email.data,
            user_id=user.id
        )
        db.session.add(student)
        db.session.commit()
        
        flash(f'Student registered successfully with Admission No: {admission_no}', 'success')
        return redirect(url_for('students_list'))
    
    return render_template('register_student.html', form=form)

# Students list route
@app.route('/students')
@login_required
def students_list():
    students = Student.query.all()
    return render_template('students_list.html', students=students)
    
# Fee Types routes
@app.route('/fee_types', methods=['GET'])
@login_required
def fee_types():
    fee_types = FeeType.query.all()
    return render_template('fee_types.html', fee_types=fee_types)

@app.route('/add_fee_type', methods=['GET', 'POST'])
@login_required
def add_fee_type():
    form = FeeTypeForm()
    if form.validate_on_submit():
        fee_type = FeeType(
            name=form.name.data,
            description=form.description.data,
            amount=form.amount.data,
            frequency=form.frequency.data
        )
        db.session.add(fee_type)
        db.session.commit()
        flash('Fee type added successfully!', 'success')
        return redirect(url_for('fee_types'))
    return render_template('add_fee_type.html', form=form)

# Payment routes
@app.route('/make_payment', methods=['GET', 'POST'])
@login_required
def make_payment():
    form = PaymentForm()
    form.student_id.choices = [(s.id, f"{s.admission_no} - {s.name}") for s in Student.query.all()]
    form.fee_type_id.choices = [(f.id, f"{f.name} - ${f.amount}") for f in FeeType.query.all()]
    
    if form.validate_on_submit():
        fee_type = FeeType.query.get(form.fee_type_id.data)
        payment = Payment(
            student_id=form.student_id.data,
            fee_type_id=form.fee_type_id.data,
            amount=form.amount.data or fee_type.amount,
            payment_method=form.payment_method.data,
            reference_no=form.reference_no.data,
            month=form.month.data,
            year=form.year.data,
            status='paid'
        )
        db.session.add(payment)
        db.session.commit()
        flash('Payment recorded successfully!', 'success')
        return redirect(url_for('payments_list'))
    
    # Pre-populate the year field with current year
    if not form.year.data:
        form.year.data = datetime.now().year
    
    return render_template('make_payment.html', form=form)

@app.route('/payments')
@login_required
def payments_list():
    payments = Payment.query.order_by(Payment.payment_date.desc()).all()
    return render_template('payments_list.html', payments=payments)

@app.route('/payment_status/<int:student_id>')
@login_required
def payment_status(student_id):
    student = Student.query.get_or_404(student_id)
    payments = Payment.query.filter_by(student_id=student_id).order_by(Payment.payment_date.desc()).all()
    return render_template('payment_status.html', student=student, payments=payments)

@app.route('/reports')
@login_required
def reports():
    # Example: Aggregate data for a report
    total_payments = db.session.query(db.func.sum(Payment.amount)).scalar() or 0
    student_count = Student.query.count()
    recent_payments = Payment.query.order_by(Payment.payment_date.desc()).limit(5).all()
    return render_template('reports.html', 
                          total_payments=total_payments,
                          student_count=student_count,
                          recent_payments=recent_payments)
                          
if __name__ == '__main__':
    app.run(debug=True)