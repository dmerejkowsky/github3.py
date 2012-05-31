"""
gist.py
=======

Module which contains all the gist related material.

"""

from json import dumps
from .models import GitHubCore, BaseComment
from .user import User


class GistFile(object):
    def __init__(self, attributes):
        super(GistFile, self).__init__()

        self._raw = attributes.get('raw_url')
        self._name = attributes.get('filename')
        self._language = attributes.get('language')
        self._size = attributes.get('size')
        self._content = attributes.get('content')

    def __repr__(self):
        return '<Gist File [%s]>' % self._name

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        self._content = value

    @property
    def name(self):
        return self._name

    @property
    def lang(self):
        return self._language

    @property
    def raw_url(self):
        return self._raw

    @property
    def size(self):
        return self._size


class GistComment(BaseComment):
    def __init__(self, comment, session):
        super(GistComment, self).__init__(comment, session)

    def __repr__(self):
        return '<Gist Comment [%s]>' % self._user.login


class Gist(GitHubCore):
    def __init__(self, data, session):
        super(Gist, self).__init__(session)

        self._update_(data)

    def __repr__(self):
        return '<Gist [%s]>' % self._id

    def _update_(self, data):
        # The gist identifier
        self._id = data.get('id')
        self._desc = data.get('description')

        # e.g. https://api.github.com/gists/1
        self._api = data.get('url')
        # e.g. https://gist.github.com/1
        self._url = data.get('html_url')
        self._public = data.get('public')
        # a list of all the forks of that gist
        self._forks = data.get('forks', [])
        # e.g. git://gist.github.com/1.git
        self._pull = data.get('git_pull_url')
        # e.g. git@gist.github.com/1.git
        self._push = data.get('git_push_url')
        # date the gist was created
        self._created = self._strptime(data.get('created_at'))
        self._updated = self._strptime(data.get('updated_at'))
        self._user = User(data.get('user'), self._session)

        # Create a list of files in the gist
        self._files = []
        for file in data['files']:
            self._files.append(GistFile(data['files'][file]))

    def create_comment(self, body):
        """Create a comment on this gist."""
        url = self._api + '/comments'
        json = self._post(url, dumps({'body': body}))
        return GistComment(json, self._session) if json else None

    @property
    def created(self):
        return self._created

    def delete(self):
        """Delete this gist."""
        return self._delete(self._api)

    @property
    def description(self):
        return self._desc

    def edit(self, **kwargs):
        """Edit this gist.

        :param kwargs: Should be either (or both) description or files.
        """
        resp = self._patch(self._api, dumps(kwargs))
        if resp.status_code == 200:
            self._update_(resp.json)
            return True
        return False

    @property
    def files(self):
        return self._files

    def fork(self):
        url = self._api + '/fork'
        json = self._post(url)
        return Gist(json) if json else None

    @property
    def forks(self):
        return self._forks

    def get(self):
        """GET /gists/:id"""
        resp = self._get(self._api)
        if resp.status_code == 200:
            self._update_(resp.json)
            return True
        return False

    @property
    def git_pull(self):
        return self._pull

    @property
    def git_push(self):
        return self._push

    @property
    def html_url(self):
        return self._url

    def is_public(self):
        return self._public

    def is_starred(self):
        url = self._api + '/star'
        resp = self._get(url)
        if resp.status_code == 204:
            return True
        return False

    def list_comments(self):
        url = self._api + '/comments'
        resp = self._get(url)
        comments = []
        if resp.status_code == 200:
            for comment in resp.json:
                comments.append(GistComment(comment, self._session))
        return comments

    def star(self):
        """Star this gist."""
        url = self._api + '/star'
        return self._put(url)

    def unstar(self):
        """Un-star this gist."""
        url = self._api + '/star'
        return self._delete(url)

    @property
    def updated(self):
        return self._updated

    @property
    def user(self):
        return self._user
