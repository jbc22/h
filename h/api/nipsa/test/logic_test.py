import json
import mock

from h.api.nipsa import logic


@mock.patch("h.api.nipsa.models.NipsaUser")
def test_index_with_no_users(NipsaUser):
    NipsaUser.all.return_value = []

    assert logic.index() == []


@mock.patch("h.api.nipsa.models.NipsaUser")
def test_index_with_one_user(NipsaUser):
    nipsa_user = mock.Mock()
    nipsa_user.user_id = "test_id"
    NipsaUser.all.return_value = [nipsa_user]

    assert logic.index() == ["test_id"]


@mock.patch("h.api.nipsa.models.NipsaUser")
def test_index_with_multiple_users(NipsaUser):
    nipsa_user1 = mock.Mock()
    nipsa_user1.user_id = "test_id1"
    nipsa_user2 = mock.Mock()
    nipsa_user2.user_id = "test_id2"
    nipsa_user3 = mock.Mock()
    nipsa_user3.user_id = "test_id3"
    NipsaUser.all.return_value = [nipsa_user1, nipsa_user2, nipsa_user3]

    assert logic.index() == ["test_id1", "test_id2", "test_id3"]


@mock.patch("h.api.nipsa.models.NipsaUser")
def test_nipsa_gets_user_by_id(NipsaUser):
    logic.nipsa(request=mock.Mock(), user_id="test_id")

    NipsaUser.get_by_id.assert_called_once_with("test_id")


@mock.patch("h.api.nipsa.models.NipsaUser")
def test_nipsa_does_not_add_when_user_already_exists(NipsaUser):
    """
    nipsa() should not call db.add() if the user already exists.
    """
    request = mock.Mock()
    nipsa_user = mock.Mock()
    NipsaUser.get_by_id.return_value = nipsa_user

    logic.nipsa(request=request, user_id="test_id")

    assert not request.db.add.called


@mock.patch("h.api.nipsa.logic._publish")
@mock.patch("h.api.nipsa.models.NipsaUser")
def test_nipsa_publishes_when_user_already_exists(
        NipsaUser, _publish):
    """
    Even if the user is already NIPSA'd, nipsa() should still publish a
    "nipsa" message to the queue.
    """
    nipsa_user = mock.Mock()
    NipsaUser.get_by_id.return_value = nipsa_user
    request = mock.Mock()

    logic.nipsa(request=request, user_id="test_id")

    _publish.assert_called_once_with(
        request, json.dumps({"action": "nipsa", "user_id": "test_id"}))
    NipsaUser.get_by_id.assert_called_once_with("test_id")


@mock.patch("h.api.nipsa.models.NipsaUser")
def test_nipsa_adds_user_if_user_does_not_exist(NipsaUser):
    request = mock.Mock()

    nipsa_user = mock.Mock()
    NipsaUser.return_value = nipsa_user

    NipsaUser.get_by_id.return_value = None

    logic.nipsa(request=request, user_id="test_id")

    NipsaUser.assert_called_once_with("test_id")
    request.db.add.assert_called_once_with(nipsa_user)


@mock.patch("h.api.nipsa.logic._publish")
@mock.patch("h.api.nipsa.models.NipsaUser")
def test_nipsa_publishes_if_user_does_not_exist(NipsaUser, _publish):
    request = mock.Mock()

    nipsa_user = mock.Mock()
    nipsa_user.user_id = "test_id"
    NipsaUser.return_value = nipsa_user

    NipsaUser.get_by_id.return_value = None

    logic.nipsa(request=request, user_id="test_id")

    _publish.assert_called_once_with(
        request, json.dumps({"action": "nipsa", "user_id": "test_id"}))


@mock.patch("h.api.nipsa.models.NipsaUser")
def test_unnipsa_gets_user_by_id(NipsaUser):
    request = mock.Mock()
    request.matchdict = {"user_id": "test_id"}

    logic.unnipsa(request=request, user_id="test_id")

    NipsaUser.get_by_id.assert_called_once_with("test_id")


@mock.patch("h.api.nipsa.models.NipsaUser")
def test_unnipsa_does_not_delete_user_that_does_not_exist(NipsaUser):
    """
    unnipsa() should not call db.delete() if the user isn't NIPSA'd.
    """
    NipsaUser.get_by_id.return_value = None
    request = mock.Mock()

    logic.unnipsa(request=request, user_id="test_id")

    assert not request.db.delete.called


@mock.patch("h.api.nipsa.logic._publish")
@mock.patch("h.api.nipsa.models.NipsaUser")
def test_unnipsa_publishes_when_user_does_not_exist(NipsaUser, _publish):
    """
    Even if the user is not NIPSA'd, unnipsa() should still publish an
    "unnipsa" message to the queue.
    """
    NipsaUser.get_by_id.return_value = None
    request = mock.Mock()

    logic.unnipsa(request=request, user_id="test_id")

    _publish.assert_called_once_with(
        request, json.dumps({"action": "unnipsa", "user_id": "test_id"}))


@mock.patch("h.api.nipsa.models.NipsaUser")
def test_unnipsa_deletes_user(NipsaUser):
    request = mock.Mock()

    nipsa_user = mock.Mock()
    nipsa_user.user_id = "test_id"
    NipsaUser.get_by_id.return_value = nipsa_user

    logic.unnipsa(request=request, user_id="test_id")

    request.db.delete.assert_called_once_with(nipsa_user)


@mock.patch("h.api.nipsa.logic._publish")
@mock.patch("h.api.nipsa.models.NipsaUser")
def test_unnipsa_publishes_if_user_exists(NipsaUser, _publish):
    request = mock.Mock()

    nipsa_user = mock.Mock()
    nipsa_user.user_id = "test_id"
    NipsaUser.get_by_id.return_value = nipsa_user

    logic.unnipsa(request=request, user_id="test_id")

    _publish.assert_called_once_with(
        request, json.dumps({"action": "unnipsa", "user_id": "test_id"}))


@mock.patch("h.api.nipsa.models.NipsaUser")
def test_is_nipsad_gets_user_by_id(NipsaUser):
    logic.is_nipsad(user_id="test_id")

    NipsaUser.get_by_id.assert_called_once_with("test_id")


@mock.patch("h.api.nipsa.models.NipsaUser")
def test_is_nipsad_returns_True_if_user_is_nipsad(NipsaUser):
    nipsa_user = mock.Mock()
    nipsa_user.user_id = "test_id"
    NipsaUser.get_by_id.return_value = nipsa_user

    assert logic.is_nipsad(user_id="test_id") is True


@mock.patch("h.api.nipsa.models.NipsaUser")
def test_is_nipsad_returns_False_if_user_is_not_nipsad(NipsaUser):
    NipsaUser.get_by_id.return_value = None

    assert logic.is_nipsad(user_id="test_user") is False
