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


def get_file_name(img_obj):
    return img_obj['title'] + '-' + str(g.user['id'])


def get_file_path(img_obj):
    file_type = img_obj['file_type']
    file_name = get_file_name(img_obj)
    return os.path.join(repo.root_path, 'static/' + secure_filename(
        file_name + file_type))


def binary_to_image(row):
    img_obj = dict(row)
    file_data = img_obj['img_data']
    file_path = get_file_path(img_obj)
    file_name = get_file_name(img_obj)
    with open(file_path, "wb") as outfile:
        outfile.write(file_data)
    img_obj['name'] = file_name
    return img_obj


@repo.route('/')
@login_required
def index():
    db = get_db()
    db.execute(
        'SELECT i.id, i.title, i.img_data, i.file_type, i.created'
        ' FROM img i JOIN users u ON i.owner_id = u.id'
        ' ORDER BY i.created DESC'
    )
    imgs = db.fetchall()
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
                "INSERT INTO img (title, img_data, file_type, owner_id)"
                " VALUES ('{}', E'{}', '{}', {})".format(
                    title, img_data, file_type, g.user['id'])
            )
            return redirect(url_for('imgRepo.index'))

    return render_template('img_repo/create.html')


def check_img_exists(id, check_author=True):
    db = get_db()
    db.execute(
        'SELECT i.id, i.title, i.img_data, i.file_type, i.created, i.owner_id'
        ' FROM img i JOIN users u ON i.owner_id = u.id'
        ' WHERE i.id = {}'.format(id)
    )
    img = db.fetchone()

    if img is None:
        abort(404, "Image doesn't exist.")
        return False

    if check_author and img['owner_id'] != g.user['id']:
        abort(403)
        return False

    return img


@repo.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    img = check_img_exists(id)

    if img:
        file_path = get_file_path(dict(img))
        db = get_db()
        db.execute("DELETE FROM img WHERE id = {}".format(id))
        if os.path.exists(file_path):
            os.remove(file_path)

        return redirect(url_for('imgRepo.index'))
