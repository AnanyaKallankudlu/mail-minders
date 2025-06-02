from collections import Counter
from datetime import datetime, timedelta, timezone
import matplotlib.pyplot as plt
from dateutil import parser
from io import BytesIO
import base64

def generate_user_bar_chart(tasks: list) -> str:
    now = datetime.now(timezone.utc)
    seven_days_ago = now - timedelta(days=7)
    bar_chart_img = None

    def parse_dt(dt_str):
        dt = parser.parse(dt_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt

    # Completed tasks in the last 7 days
    filtered = [
        task for task in tasks
        if task['completed_at'] and parse_dt(task['completed_at']) >= seven_days_ago
    ]

    # Bar chart for completed tasks
    if filtered:
        category_counts = Counter(task['category'] for task in filtered)
        if not category_counts:
            category_counts = {"No Data": 1}
        categories = list(category_counts.keys())
        counts = list(category_counts.values())
        bar_chart_img = generate_bar_chart(categories, counts)

    # Remaining (not completed) tasks
    remaining = [
        task for task in tasks
        if not task['completed_at']
    ]

    # Pie chart for remaining tasks
    remaining_counts = Counter(task['category'] for task in remaining)
    if not remaining_counts:
        remaining_counts = {"No Data": 1}
    remaining_categories = list(remaining_counts.keys())
    remaining_sizes = list(remaining_counts.values())
    pie_chart_img = generate_pie_chart(remaining_categories, remaining_sizes)

    return bar_chart_img, pie_chart_img

def generate_pie_chart(categories, task_counts):
    cmap = plt.get_cmap('tab20')
    pie_colors = [cmap(i % cmap.N) for i in range(len(categories))]
    plt.figure(figsize=(7, 7))
    plt.pie(
        task_counts,
        labels=categories,
        autopct='%1.1f%%',
        startangle=140,
        colors=pie_colors
    )
    buf = BytesIO()
    plt.title('Remaining Tasks by Category')
    plt.tight_layout()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')


def generate_bar_chart(categories, task_counts):
    cmap = plt.get_cmap('tab20')
    colors = [cmap(i % cmap.N) for i in range(len(categories))]
    plt.figure(figsize=(8, 6))
    bars = plt.bar(categories, task_counts, color=colors)
    plt.title('Tasks Completed by Category (Last 7 Days)')
    plt.xlabel('Category')
    plt.ylabel('Tasks Completed')
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval + 0.2, int(yval), ha='center', va='bottom')
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')
