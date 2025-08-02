from flask import Blueprint,flash, session,render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,current_user,login_required,logout_user
from ..forms import LoginForm, RegisterForm, CreateGroupForm
from ..models import User, Group,Expense,ExpenseSplit,Membership
from datetime import datetime
from ..extensions import db

# Create the blueprint
main = Blueprint('main', __name__)

# Home route
@main.route('/')
def home():
    return redirect('/login')

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('register.html', form=form)

        # Create user
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        print("ok")
        return redirect(url_for('main.dashboard'))

    return render_template('register.html', form=form)
@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.dashboard'))

    return render_template('login.html', form=form)

@main.route('/dashboard')
@login_required
def dashboard():
    # Query all groups created by the logged-in user
    user_groups = Group.query.filter_by(created_by=current_user.id).all()
    memberships = Membership.query.filter_by(user_id=current_user.id).all()
    joined_group_ids = [m.group_id for m in memberships]
    joined_groups = Group.query.filter(Group.id.in_(joined_group_ids)).all()

    return render_template(
        'dashboard.html',
        username=current_user.username,
        groups=user_groups
    )


@main.route('/submit', methods=['GET', 'POST'])
def submit_bill():
    if request.method == 'POST':
        bill_text = request.form.get('bill_text')
        return f"✅ Received bill: {bill_text}"
    return '''
        <form method="POST">
            <textarea name="bill_text" placeholder="Enter your bill here..."></textarea>
            <br>
            <button type="submit">Submit</button>
        </form>
    '''

# @main.route('/new-bill', methods=['GET', 'POST'])
# def new_bill():
#     if request.method == 'POST':
#       if request.method == 'POST':
#         bill_text = request.form.get('bill_text')
#         parsed_data = parse_bill_text(bill_text)  # You'll write this function
#         print(parsed_data)  # For now, just test it
#         return render_template('results.html', parsed_data=parsed_data)

#     return render_template('new_bill.html')


@main.route('/create_group', methods=['GET', 'POST'])
@login_required
def create_group():
    form = CreateGroupForm()
    if form.validate_on_submit():
        new_group = Group(
            name=form.name.data,
            created_by=current_user.id,
            created_at=datetime.utcnow(),
            description=form.description.data,
            num_members=form.num_members.data
        )
        db.session.add(new_group)
        db.session.commit()
 
        return redirect(url_for('upload.upload_receipt', group_id=new_group.id))
    

    return render_template('create_group.html', form=form)


# @main.route('/groups')
# @login_required
# def groups():
#     user_groups = Group.query.filter_by(created_by=current_user.id).all()
#     return render_template('groups.html', groups=user_groups)
@main.route('/group/<int:group_id>',methods=['GET', 'POST'])
@login_required
def group_detail(group_id):
    group = Group.query.get_or_404(group_id)

    # Handle form submission if user changed a dropdown
    if request.method == 'POST':
        split_id = request.form.get('split_id')
        new_status = request.form.get('status')

        if split_id and new_status in ['paid', 'unpaid']:
            split = ExpenseSplit.query.get(int(split_id))
            if split:
                split.status = new_status
                db.session.commit()


    # Regular data fetch and render
    expense = Expense.query.filter_by(group_id=group.id).first()
    payment_info = []

    if expense:
        splits = ExpenseSplit.query.filter_by(expense_id=expense.id).all()

        for split in splits:
            if split.user_id:
                user = User.query.get(split.user_id)
                name = user.username if user else "Unknown User"
            else:
                name = split.guest_name or "Guest"

            payment_info.append({
                'id': split.id,
                'username': name,
                'amount': split.amount,
                'status': split.status
            })

    return render_template('group_detail.html', group=group, payment_info=payment_info)

@main.route('/manual/<int:group_id>', methods=['POST', 'GET'])
@login_required
def manual_form(group_id):
    print("umm")
    group = Group.query.get_or_404(group_id)
    
    if request.method == 'POST':
        data = request.form
        members = data.getlist('members')

        paid_by_index = request.form.get("paid_by")
        paid_by_name = request.form.get(f"members[{paid_by_index}][name]") 

        expense = Expense(
            group_id=group.id,
            payer_id="None",
            amount=0,
            tax=request.form.get("tax"),
            title="something")
            
        db.session.add(expense)
        db.session.flush()
        print("here")
        for i in range(group.num_members):
            member_prefix = f"members[{i}]"
            member_name = data.get(f"{member_prefix}[name]")
            
            # ✅ Create Membership as guest
            membership = Membership(
                guest_name=member_name,
                group_id=group.id,
                is_guest=True
            )
            db.session.add(membership)
            db.session.flush()  # so we can get the membership ID

            j = 0
            amount=0
            while True:
                item_name = data.get(f"{member_prefix}[items][{j}][name]")
                print("name:{item_name}")
                if not item_name:
                    break  # no more items

                amount+=(float(data.get(f"{member_prefix}[items][{j}][price]"))*float(data.get(f"{member_prefix}[items][{j}][share]")))
                j += 1
            amount+=(float(request.form.get("tax"))/int(group.num_members))
            expense_split = ExpenseSplit(
                expense_id=expense.id,
                amount=amount,  # calculating share
                user_id=None,  # unknown until guest logs in
                status="unpaid",
                guest_name=member_name
            )
            db.session.add(expense_split)
            print("added for:"+member_name)

# Get the correct name: guest or real user
            if membership and membership.is_guest:
                name = membership.guest_name or "Guest"
            else:
                user = User.query.get(user_id)
                name = user.username if user else "Unknown User"


            print(f"✅ Added ExpenseSplit for: {name} — ₹{amount}")
        db.session.commit()

        return redirect(url_for('main.dashboard'))

    return render_template('manual_form.html', group_id=group_id,group=group)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))  # or wherever your login route is

# @main.route('/manual_form/<int:group_id>', methods=['POST'])
# @login_required
# def submit_manual_form(group_id):
#     members_data = []

#     # Get number of members from hidden input
#     num_members = int(request.form.get('num_members', 0))

#     for m in range(num_members):
#         member_name = request.form.get(f'member_{m}_name')
#         if not member_name:
#             continue

#         member_items = []
#         item_index = 0
#         while True:
#             item_name = request.form.get(f'member_{m}_item_{item_index}_name')
#             item_price = request.form.get(f'member_{m}_item_{item_index}_price')
#             item_share = request.form.get(f'member_{m}_item_{item_index}_share')

#             if not item_name:
#                 break  # No more items for this member

#             try:
#                 item_price = float(item_price)
#                 item_share = float(item_share)
#             except (ValueError, TypeError):
#                 item_price = 0
#                 item_share = 1

#             member_items.append({
#                 "name": item_name,
#                 "price": item_price,
#                 "share": item_share
#             })
#             item_index += 

#         members_data.append({
#             "name": member_name,
#             "items": member_items
#         })

#     # (Optional) Print or log it for testing
#     print("Parsed Manual Form Data:", members_data)

#     # TODO: Save to DB or pass to template
#     flash("Form submitted successfully!", "success")
#     return redirect(url_for('main.dashboard'))
@main.route('/join/<invite_code>')
@login_required
def join_group(invite_code):
    group = Group.query.filter_by(invite_code=invite_code).first_or_404()
    user = current_user

    # Check if already a member
    existing = Membership.query.filter_by(user_id=user.id, group_id=group.id).first()
    if existing:
        return redirect(url_for('main.group_detail', group_id=group.id))

    # Step 1: Try full match on guest name
    guest_match = Membership.query.filter_by(group_id=group.id, guest_name=user.username, is_guest=True).first()

    if guest_match:
        guest_match.user_id = user.id
        guest_match.is_guest = False
        guest_match.status = "member"
        db.session.commit()
        return redirect(url_for('main.group_detail', group_id=group.id))

    # Step 2: Try partial match on guest name
    partial_match = Membership.query.filter(
        Membership.group_id == group.id,
        Membership.is_guest == True,
        Membership.guest_name.ilike(f"%{user.username}%")
    ).first()

    if partial_match:
        partial_match.user_id = user.id
        partial_match.is_guest = False
        partial_match.status = "member"
        db.session.commit()
        flash("Joined group by partial guest name match.", "success")
        return redirect(url_for('main.group_detail', group_id=group.id))

    # Step 3: Create new membership
    new_member = Membership(
        user_id=user.id,
        group_id=group.id,
        is_guest=False,
        status="member"
    )
    db.session.add(new_member)
    db.session.commit()
    return redirect(url_for('main.group_detail', group_id=group.id))

@main.route('/join_code', methods=['POST'])
@login_required
def join_by_code():
    invite_code = request.form.get('invite_code')
    if not invite_code:
        flash("No invite code provided.", "error")
        return redirect(url_for('main.dashboard'))

    # Reuse the same logic as the /join/<invite_code> route
    return redirect(url_for('main.join_group', invite_code=invite_code))
