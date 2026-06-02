import copy

from fastapi.testclient import TestClient

from src.app import activities, app

original_activities = copy.deepcopy(activities)
client = TestClient(app)


def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def test_root_redirects_to_static_index():
    # Arrange
    reset_activities()
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_activity_list():
    # Arrange
    reset_activities()

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert response.json()["Programming Class"]["max_participants"] == 20


def test_signup_for_activity_adds_new_participant():
    # Arrange
    reset_activities()
    activity_name = "Art Workshop"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for {activity_name}"
    }

    participant_list = client.get("/activities").json()[activity_name]["participants"]
    assert email in participant_list


def test_signup_for_activity_rejects_duplicate_signup():
    # Arrange
    reset_activities()
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": existing_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_removes_existing_student():
    # Arrange
    reset_activities()
    activity_name = "Soccer Team"
    email = "nina@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Removed {email} from {activity_name}"
    }

    participants = client.get("/activities").json()[activity_name]["participants"]
    assert email not in participants


def test_remove_participant_missing_student_returns_404():
    # Arrange
    reset_activities()
    activity_name = "Drama Club"
    missing_email = "absent@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": missing_email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
