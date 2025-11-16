
import requests
import time
import os

def test_upload():
    # 1. Arrange: Create a dummy file for upload.
    with open("test.csv", "w") as f:
        f.write("col1,col2\n1,2\n3,4")

    # 2. Act: Upload the file.
    with open("test.csv", "rb") as f:
        response = requests.post("http://127.0.0.1:5000/upload", files={"file": f})

    # 3. Assert: Check that the upload was successful and a task ID was returned.
    assert response.status_code == 200
    task_id = response.json().get("task_id")
    assert task_id

    # 4. Act: Poll the status endpoint until the analysis is complete.
    while True:
        status_response = requests.get(f"http://127.0.0.1:5000/status/{task_id}")
        assert status_response.status_code == 200
        status = status_response.json().get("status")
        if status == "complete":
            break
        elif status == "error":
            raise Exception("Analysis failed")
        time.sleep(1)

    # 5. Assert: Check that the report was generated.
    report_response = requests.get(f"http://127.0.0.1:5000/report/{task_id}")
    assert report_response.status_code == 200
    assert "Data Analysis Report" in report_response.text

    print("Test passed!")

if __name__ == "__main__":
    test_upload()
