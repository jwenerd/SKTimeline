
from sktimeline import *
from sktimeline.views import login_required, page_not_found
from wtforms import validators

GithubForm = model_form(GithubFeedSetting, Form, exclude=['user','feed_items'], field_args = {
 #todo add basic validation
 'username' : {
      'validators' : [validators.Required()]
  },
 'project' : {
      'validators' : [validators.Required()]
  }
})

@app.route('/dashboard/github/new',methods=['GET','POST'])
@login_required
def dashboard_github_new(id=None):
    model = GithubFeedSetting()
    form = GithubForm(request.form, model)

    if request.method == 'POST' and form.validate():
        form.populate_obj(model)
        model.status = 'new'
        model.user = User.query.get(session['user_id'])
        db.session.add(model)
        db.session.commit()
        db.session.close()

        flash("GitHub entry added.")
        return redirect(url_for("dashboard") + '#github')

    return render_template("dashboard/github.html", form = form)


@app.route('/dashboard/github/edit/<id>',methods=['GET','POST'])
@login_required
def dashboard_github_edit(id):
    model = GithubFeedSetting.query.get(id)
    if not(model) or model.user_id != session['user_id']:
        return page_not_found()

    form = GithubForm(request.form, model)

    if request.method == 'POST' and request.form.has_key('delete'):
        db.session.delete(model)
        db.session.commit()
        db.session.close()
        flash("Github entry deleted.")
        return redirect(url_for("dashboard") + '#github')

    return render_template("dashboard/github.html", form = form, edit = True)
