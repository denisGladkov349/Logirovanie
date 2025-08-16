from datetime import datetime
from collections import defaultdict
from argparse import ArgumentParser
from json import loads, JSONDecodeError
from sys import exit, stderr
from tabulate import tabulate


def parse_args():
    parser = ArgumentParser(description='Process log files and generate reports.')
    parser.add_argument('--file', action='append', required=True, help='Log file path(s)')
    parser.add_argument('--report', choices=['average'], required=True, help='Report type')
    parser.add_argument('--date', help='Filter logs by date (YYYY-MM-DD)')
    return parser.parse_args()


def read_logs(files, filter_date=None):
    endpoint_data = defaultdict(lambda: {'count': 0, 'total_time': 0.0})
    for file_path in files:
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    try:
                        log_entry = loads(line)
                        process_log_entry(log_entry, endpoint_data, filter_date)
                    except JSONDecodeError:
                        continue
        except FileNotFoundError:
            print(f"Error: File not found - {file_path}", file=stderr)
            exit(1)
    return endpoint_data


def process_log_entry(log_entry, endpoint_data, filter_date):
    timestamp = log_entry.get('@timestamp', '')
    url = log_entry.get('url')
    response_time = log_entry.get('response_time')
    if not all([timestamp, url, isinstance(response_time, (int, float))]):
        return
    if filter_date:
        try:
            log_date = datetime.fromisoformat(timestamp).date().isoformat()
            if log_date != filter_date:
                return
        except ValueError:
            return
    endpoint_data[url]['count'] += 1
    endpoint_data[url]['total_time'] += response_time


def generate_average_report(endpoint_data):
    report = []
    for endpoint, data in endpoint_data.items():
        avg_time = data['total_time'] / data['count'] if data['count'] > 0 else 0
        report.append((endpoint, data['count'], round(avg_time, 3)))
    return sorted(report, key=lambda x: x[0])  # Sort by endpoint


def print_report(report):
    try:
        headers = ["Endpoint", "Count", "Avg Time"]
        print(tabulate(report, headers=headers, tablefmt="grid"))
    except ImportError:
        print("Endpoint\tCount\tAvg Time")
        for row in report:
            print(f"{row[0]}\t{row[1]}\t{row[2]}")


def main():
    args = parse_args()
    endpoint_data = read_logs(args.file, args.date)
    if args.report == 'average':
        report = generate_average_report(endpoint_data)
        print_report(report)


if __name__ == "__main__":
    main()