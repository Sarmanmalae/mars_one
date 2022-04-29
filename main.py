from flask import Flask, render_template
from flask_login import LoginManager, login_user, login_required, logout_user
from werkzeug.utils import redirect

from data import db_session
from data.jobs import Jobs
from data.users import User
from data.departments import Department
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
    jobs = []
    ids = []
    teamleads = []
    db_sess = db_session.create_session()
    for job in db_sess.query(Jobs).all():
        jobs.append(job)
        ids.append(job.team_leader)
    for i in ids:
        for user in db_sess.query(User).filter(User.id.like(i)):
            teamleads.append(user.surname + ' ' + user.name)
    return render_template('index.html', js=jobs, tl=teamleads)


@app.route('/delete_job/<int:num>', methods=['GET', 'POST'])
def delete(num):
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).filter(Jobs.id == num).first()
    db_sess.delete(job)
    db_sess.commit()
    return redirect('/')


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
        job.job = form.job.data
        job.work_hours = form.work_hours.data
        job.collaborators = form.collaborators.data
        job.is_finished = form.is_finished.data
        db_sess.commit()
        return redirect('/')

    job = db_sess.query(Jobs).filter(Jobs.id == num).first()
    info = {'job': job.job, 'team_leader': job.team_leader, 'work_hours': job.work_hours,
            'collaborators': job.collaborators, 'is_finsished': job.is_finished}
    return render_template('edit_job.html', title='Editing a job', form=form, info=info)


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
            is_finished=form.is_finished.data
        )
        db_sess.add(job)
        db_sess.commit()
        return redirect('/')
    return render_template('job_adding.html', title='Adding a job', form=form)


if __name__ == '__main__':
    main()
