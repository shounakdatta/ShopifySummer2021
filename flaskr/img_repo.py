from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from flaskr.auth import login_required
from flaskr.db import get_db
from typing import IO
import os

repo = Blueprint('imgRepo', __name__)


def binary_to_image(row):
    img_obj = dict(row)
    file_type = img_obj['file_type']
    file_name = img_obj['title'] + '-' + str(g.user['id'])
    file_data = img_obj['img_data']
    file_path = os.path.join(repo.root_path, 'static/' + secure_filename(
        file_name + file_type))
    print(file_path, file_name, file_type)
    with open(file_path, "wb") as outfile:
        outfile.write(file_data)
    img_obj['path'] = file_path
    return img_obj


@repo.route('/')
@login_required
def index():
    db = get_db()
    imgs = db.execute(
        'SELECT i.id, i.title, i.img_data, i.file_type, i.created'
        ' FROM img i JOIN user u ON i.owner_id = u.id'
        ' ORDER BY i.created DESC'
    ).fetchall()
    saved_imgs = map(binary_to_image, imgs)
    return render_template('img_repo/index.html', imgs=saved_imgs)


@repo.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        img_file: IO = request.files['imgFile']
        error = None

        if not img_file:
            error = 'Image file is required.'

        if error is not None:
            flash(error)
        else:
            img_data = img_file.read()
            file_name = img_file.filename
            title, file_type = os.path.splitext(file_name)
            print(title, file_type)
            db = get_db()
            db.execute(
                'INSERT INTO img (title, img_data, file_type, owner_id)'
                ' VALUES (?, ?, ?, ?)',
                (title, img_data, file_type, g.user['id'])
            )
            db.commit()
            return redirect(url_for('imgRepo.index'))

    return render_template('img_repo/create.html')


def check_img_exists(id, check_author=True):
    img = get_db().execute(
        'SELECT i.id, owner_id'
        ' FROM img i JOIN user u ON i.owner_id = u.id'
        ' WHERE i.id = ?',
        (id,)
    ).fetchone()

    if img is None:
        abort(404, "Image doesn't exist.")
        return False

    if check_author and img['owner_id'] != g.user['id']:
        abort(403)
        return False

    return True


@repo.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    img_exists = check_img_exists(id)

    if img_exists:
        db = get_db()
        db.execute('DELETE FROM img WHERE id = ?', (id,))
        db.commit()
        return redirect(url_for('imgRepo.index'))
