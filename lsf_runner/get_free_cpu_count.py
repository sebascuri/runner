"""Python Script Template."""
import psutil

if __name__ == "__main__":
    cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
    print(len(list(filter(lambda x: x < 25, cpu_percent))))
