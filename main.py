from flask import Flask, render_template
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import redirect

from data import db_session
from data.category import Category
from data.jobs import Jobs
from data.users import User
from data.departments import Department
from forms.Dep_adding import DepartmentAddingForm
from forms.Job_adding import JobAddingForm
from forms.login import LoginForm
from forms.register import RegisterForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/mars_explorer.db")
    app.run()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def main_page():
    db_sess = db_session.create_session()
    jobs = []
    ids = []
    teamleads = []
    cs = []
    for job in db_sess.query(Jobs).all():
        jobs.append(job)
        cs.append(job.categories[0])
        ids.append(job.team_leader)
    print(cs)
    for i in ids:
        for user in db_sess.query(User).filter(User.id.like(i)):
            teamleads.append(user.surname + ' ' + user.name)
    return render_template('index.html', js=jobs, tl=teamleads, cs=cs)


@app.route('/departments')
def dp():
    deps = []
    chief = []
    chiefs = []
    db_sess = db_session.create_session()
    for dep in db_sess.query(Department).all():
        deps.append([dep.chief, dep.title, dep.members, dep.email, dep.id, dep.chief])
        chief.append(dep.chief)
    for i in range(len(deps)):
        for user in db_sess.query(User).filter(User.id == deps[i][0]):
            deps[i][0] = user.surname + ' ' + user.name
    return render_template('departments.html', deps=deps)


@app.route('/delete_department/<int:num>', methods=['GET', 'POST'])
def delete_d(num):
    db_sess = db_session.create_session()
    dep = db_sess.query(Department).filter(Department.id == num).first()
    db_sess.delete(dep)
    db_sess.commit()
    return redirect('/departments')


@app.route('/delete_job/<int:num>', methods=['GET', 'POST'])
def delete(num):
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).filter(Jobs.id == num).first()
    job.categories.remove(job.categories[0])
    db_sess.delete(job)
    db_sess.commit()
    return redirect('/')


@app.route('/edit_department/<int:num>', methods=['GET', 'POST'])
def edit_d(num):
    form = DepartmentAddingForm()
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        dep = db_sess.query(Department).filter(Department.id == num).first()
        dep.title = form.title.data
        dep.chief = form.chief_id.data
        dep.members = form.members.data
        dep.email = form.email.data
        db_sess.commit()
        return redirect('/departments')

    dp = db_sess.query(Department).filter(Department.id == num).first()
    info = {'title': dp.title, 'chief_id': dp.chief, 'members': dp.members,
            'email': dp.email}
    return render_template('edit_department.html', title='Editing a job', form=form, info=info)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            surname=form.surname.data,
            age=form.age.data,
            position=form.position.data,
            speciality=form.speciality.data,
            address=form.address.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/edit_job/<int:num>', methods=['GET', 'POST'])
def edit_job(num):
    form = JobAddingForm()
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        job = db_sess.query(Jobs).filter(Jobs.id == num).first()
        job.categories.remove(job.categories[0])
        c = db_sess.query(Category).filter(Category.num == form.category.data).first()
        job.categories.append(c)
        job.job = form.job.data
        job.work_hours = form.work_hours.data
        job.team_leader = form.team_leader.data
        job.collaborators = form.collaborators.data
        job.is_finished = form.is_finished.data
        db_sess.commit()
        return redirect('/')

    job = db_sess.query(Jobs).filter(Jobs.id == num).first()
    info = {'job': job.job, 'team_leader': job.team_leader, 'work_hours': job.work_hours,
            'collaborators': job.collaborators, 'is_finsished': job.is_finished}
    hc = job.categories[0].num
    return render_template('edit_job.html', title='Editing a job', form=form, info=info, hc=hc)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/addjob', methods=['GET', 'POST'])
def addjob():
    form = JobAddingForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        job = Jobs(
            job=form.job.data,
            team_leader=form.team_leader.data,
            work_hours=form.work_hours.data,
            collaborators=form.collaborators.data,
            is_finished=form.is_finished.data,
            creator=current_user.id
        )
        db_sess.add(job)
        db_sess.commit()
        db_sess = db_session.create_session()
        c = db_sess.query(Category).filter(Category.num == form.category.data).first()
        j = db_sess.query(Jobs).filter(Jobs.job == form.job.data).first()
        j.categories.append(c)
        db_sess.commit()
        return redirect('/')
    return render_template('job_adding.html', title='Adding a job', form=form)


@app.route('/add_department', methods=['GET', 'POST'])
def add_d():
    form = DepartmentAddingForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        dep = Department(
            title=form.title.data,
            chief=form.chief_id.data,
            members=form.members.data,
            email=form.email.data,
        )
        db_sess.add(dep)
        db_sess.commit()
        return redirect('/departments')
    return render_template('add_department.html', title='Adding a departament', form=form)


if __name__ == '__main__':
    main()
