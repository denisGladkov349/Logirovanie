import pytest
from json import dumps
from main import read_logs, generate_average_report

@pytest.fixture
def sample_log_file(tmp_path):
    data = [
        {"@timestamp": "2025-06-22T10:00:00", "url": "/api/test", "response_time": 0.1},
        {"@timestamp": "2025-06-23T11:00:00", "url": "/api/test", "response_time": 0.2}
    ]
    file_path = tmp_path / "test.log"
    with open(file_path, 'w') as f:
        for entry in data:
            f.write(dumps(entry) + '\n')
    return file_path

def test_read_logs(sample_log_file):
    logs = read_logs([sample_log_file])
    assert "/api/test" in logs
    assert logs["/api/test"]["count"] == 2

def test_date_filter(sample_log_file):
    logs = read_logs([sample_log_file], filter_date="2025-06-22")
    assert logs["/api/test"]["count"] == 1

def test_average_report(sample_log_file):
    logs = read_logs([sample_log_file])
    report = generate_average_report(logs)
    assert report[0] == ("/api/test", 2, 0.15)