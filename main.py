from flask import Flask, render_template
from flask_login import LoginManager

from data import db_session
from data.jobs import Jobs
from data.users import User

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


if __name__ == '__main__':
    main()
